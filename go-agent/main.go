package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/host"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/process"
)

const (
	defaultPort = "8080"
	metricsPath = "/metrics"
	healthPath  = "/health"
	diagPath    = "/diagnostics"
)

var (
	version = "1.0.0"

	// Prometheus metrics
	cpuUsage = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "agent_cpu_usage_percent",
		Help: "Current CPU usage percentage",
	})

	memoryUsage = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "agent_memory_usage_percent",
		Help: "Current memory usage percentage",
	})

	diskUsage = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "agent_disk_usage_percent",
		Help: "Current disk usage percentage",
	})

	networkConnections = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "agent_network_connections",
		Help: "Number of active network connections",
	})

	portCheckResults = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "agent_port_check_result",
			Help: "Port check result (1 = open, 0 = closed)",
		},
		[]string{"port", "protocol"},
	)
)

type Diagnostics struct {
	Timestamp    time.Time              `json:"timestamp"`
	Hostname     string                 `json:"hostname"`
	OS           string                 `json:"os"`
	Architecture string                 `json:"architecture"`
	Uptime       uint64                 `json:"uptime"`
	CPU          CPUInfo                `json:"cpu"`
	Memory       MemoryInfo             `json:"memory"`
	Disk         []DiskInfo             `json:"disk"`
	Network      NetworkInfo            `json:"network"`
	Processes    int                    `json:"processes"`
	PortChecks   map[string]PortStatus `json:"port_checks"`
}

type CPUInfo struct {
	Usage     float64 `json:"usage_percent"`
	Cores     int     `json:"cores"`
	ModelName string  `json:"model_name"`
}

type MemoryInfo struct {
	Total       uint64  `json:"total_bytes"`
	Available   uint64  `json:"available_bytes"`
	Used        uint64  `json:"used_bytes"`
	UsagePercent float64 `json:"usage_percent"`
}

type DiskInfo struct {
	Device      string  `json:"device"`
	Mountpoint  string  `json:"mountpoint"`
	Total       uint64  `json:"total_bytes"`
	Used        uint64  `json:"used_bytes"`
	Free        uint64  `json:"free_bytes"`
	UsagePercent float64 `json:"usage_percent"`
}

type NetworkInfo struct {
	Interfaces []InterfaceInfo `json:"interfaces"`
	Routes     []RouteInfo     `json:"routes"`
	Connections int            `json:"connections"`
}

type InterfaceInfo struct {
	Name      string   `json:"name"`
	Addresses []string `json:"addresses"`
	Up        bool     `json:"up"`
}

type RouteInfo struct {
	Destination string `json:"destination"`
	Gateway     string `json:"gateway"`
	Interface   string `json:"interface"`
}

type PortStatus struct {
	Port     int    `json:"port"`
	Protocol string `json:"protocol"`
	Open     bool   `json:"open"`
	Service  string `json:"service,omitempty"`
}

type Agent struct {
	config Config
}

type Config struct {
	Port           string
	CheckInterval  time.Duration
	PortsToCheck   []int
	EnableMetrics  bool
}

func init() {
	prometheus.MustRegister(cpuUsage)
	prometheus.MustRegister(memoryUsage)
	prometheus.MustRegister(diskUsage)
	prometheus.MustRegister(networkConnections)
	prometheus.MustRegister(portCheckResults)
}

func main() {
	log.Printf("Starting Infrastructure Hardening Agent v%s", version)

	agent := &Agent{
		config: Config{
			Port:           getEnv("AGENT_PORT", defaultPort),
			CheckInterval:  time.Duration(getEnvInt("AGENT_CHECK_INTERVAL", 30)) * time.Second,
			PortsToCheck:   []int{22, 80, 443, 8080},
			EnableMetrics:  true,
		},
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	var wg sync.WaitGroup

	// Start HTTP server
	wg.Add(1)
	go func() {
		defer wg.Done()
		agent.startServer()
	}()

	// Start metrics collection
	if agent.config.EnableMetrics {
		wg.Add(1)
		go func() {
			defer wg.Done()
			agent.collectMetrics(ctx)
		}()
	}

	// Start periodic diagnostics
	wg.Add(1)
	go func() {
		defer wg.Done()
		agent.runPeriodicChecks(ctx)
	}()

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	// signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	log.Println("Shutting down agent...")
	cancel()
	wg.Wait()
	log.Println("Agent stopped")
}

func (a *Agent) startServer() {
	mux := http.NewServeMux()

	mux.HandleFunc(healthPath, a.healthHandler)
	mux.HandleFunc(diagPath, a.diagnosticsHandler)
	mux.Handle(metricsPath, promhttp.Handler())

	addr := ":" + a.config.Port
	log.Printf("Starting HTTP server on %s", addr)

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func (a *Agent) healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"version": version,
	})
}

func (a *Agent) diagnosticsHandler(w http.ResponseWriter, r *http.Request) {
	diagnostics, err := a.collectDiagnostics()
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(diagnostics)
}

func (a *Agent) collectDiagnostics() (*Diagnostics, error) {
	hostInfo, err := host.Info()
	if err != nil {
		return nil, fmt.Errorf("failed to get host info: %w", err)
	}

	cpuInfo, err := a.getCPUInfo()
	if err != nil {
		return nil, fmt.Errorf("failed to get CPU info: %w", err)
	}

	memInfo, err := a.getMemoryInfo()
	if err != nil {
		return nil, fmt.Errorf("failed to get memory info: %w", err)
	}

	diskInfo, err := a.getDiskInfo()
	if err != nil {
		return nil, fmt.Errorf("failed to get disk info: %w", err)
	}

	netInfo, err := a.getNetworkInfo()
	if err != nil {
		return nil, fmt.Errorf("failed to get network info: %w", err)
	}

	processes, err := process.Processes()
	if err != nil {
		return nil, fmt.Errorf("failed to get processes: %w", err)
	}

	portChecks := a.checkPorts()

	return &Diagnostics{
		Timestamp:    time.Now(),
		Hostname:     hostInfo.Hostname,
		OS:           hostInfo.OS,
		Architecture: hostInfo.KernelArch,
		Uptime:       hostInfo.Uptime,
		CPU:          cpuInfo,
		Memory:       memInfo,
		Disk:         diskInfo,
		Network:      netInfo,
		Processes:    len(processes),
		PortChecks:   portChecks,
	}, nil
}

func (a *Agent) getCPUInfo() (CPUInfo, error) {
	percent, err := cpu.Percent(time.Second, false)
	if err != nil {
		return CPUInfo{}, err
	}

	info, err := cpu.Info()
	if err != nil {
		return CPUInfo{}, err
	}

	return CPUInfo{
		Usage:     percent[0],
		Cores:     runtime.NumCPU(),
		ModelName: info[0].ModelName,
	}, nil
}

func (a *Agent) getMemoryInfo() (MemoryInfo, error) {
	memStat, err := mem.VirtualMemory()
	if err != nil {
		return MemoryInfo{}, err
	}

	return MemoryInfo{
		Total:        memStat.Total,
		Available:    memStat.Available,
		Used:         memStat.Used,
		UsagePercent: memStat.UsedPercent,
	}, nil
}

func (a *Agent) getDiskInfo() ([]DiskInfo, error) {
	partitions, err := disk.Partitions(false)
	if err != nil {
		return nil, err
	}

	var diskInfos []DiskInfo
	for _, partition := range partitions {
		usage, err := disk.Usage(partition.Mountpoint)
		if err != nil {
			continue
		}

		diskInfos = append(diskInfos, DiskInfo{
			Device:       partition.Device,
			Mountpoint:   partition.Mountpoint,
			Total:        usage.Total,
			Used:         usage.Used,
			Free:         usage.Free,
			UsagePercent: usage.UsedPercent,
		})
	}

	return diskInfos, nil
}

func (a *Agent) getNetworkInfo() (NetworkInfo, error) {
	interfaces, err := net.Interfaces()
	if err != nil {
		return NetworkInfo{}, err
	}

	var interfaceInfos []InterfaceInfo
	for _, iface := range interfaces {
		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}

		var addrStrings []string
		for _, addr := range addrs {
			addrStrings = append(addrStrings, addr.String())
		}

		interfaceInfos = append(interfaceInfos, InterfaceInfo{
			Name:      iface.Name,
			Addresses: addrStrings,
			Up:        iface.Flags&net.FlagUp != 0,
		})
	}

	routes := a.getRoutes()

	connections := a.countConnections()

	return NetworkInfo{
		Interfaces: interfaceInfos,
		Routes:     routes,
		Connections: connections,
	}, nil
}

func (a *Agent) getRoutes() []RouteInfo {
	cmd := exec.Command("ip", "route", "show")
	output, err := cmd.Output()
	if err != nil {
		return []RouteInfo{}
	}

	// Parse route output (simplified)
	lines := strings.Split(string(output), "\n")
	var routes []RouteInfo
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 3 {
			routes = append(routes, RouteInfo{
				Destination: parts[0],
				Gateway:     parts[2],
				Interface:   parts[len(parts)-1],
			})
		}
	}

	return routes
}

func (a *Agent) countConnections() int {
	cmd := exec.Command("ss", "-tun")
	output, err := cmd.Output()
	if err != nil {
		return 0
	}

	lines := strings.Split(string(output), "\n")
	return len(lines) - 1 // Subtract header
}

func (a *Agent) checkPorts() map[string]PortStatus {
	results := make(map[string]PortStatus)

	for _, port := range a.config.PortsToCheck {
		// Check TCP
		tcpOpen := a.isPortOpen(port, "tcp")
		results[fmt.Sprintf("%d/tcp", port)] = PortStatus{
			Port:     port,
			Protocol: "tcp",
			Open:     tcpOpen,
		}

		// Update Prometheus metric
		value := 0.0
		if tcpOpen {
			value = 1.0
		}
		portCheckResults.WithLabelValues(fmt.Sprintf("%d", port), "tcp").Set(value)
	}

	return results
}

func (a *Agent) isPortOpen(port int, protocol string) bool {
	address := fmt.Sprintf(":%d", port)
	conn, err := net.DialTimeout(protocol, address, 2*time.Second)
	if err != nil {
		return false
	}
	conn.Close()
	return true
}

func (a *Agent) collectMetrics(ctx context.Context) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			cpuPercent, _ := cpu.Percent(time.Second, false)
			if len(cpuPercent) > 0 {
				cpuUsage.Set(cpuPercent[0])
			}

			memStat, _ := mem.VirtualMemory()
			memoryUsage.Set(memStat.UsedPercent)

			diskStat, _ := disk.Usage("/")
			diskUsage.Set(diskStat.UsedPercent)

			connections := a.countConnections()
			networkConnections.Set(float64(connections))
		}
	}
}

func (a *Agent) runPeriodicChecks(ctx context.Context) {
	ticker := time.NewTicker(a.config.CheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			diagnostics, err := a.collectDiagnostics()
			if err != nil {
				log.Printf("Error collecting diagnostics: %v", err)
				continue
			}

			log.Printf("Diagnostics collected: CPU=%.2f%%, Memory=%.2f%%, Connections=%d",
				diagnostics.CPU.Usage,
				diagnostics.Memory.UsagePercent,
				diagnostics.Network.Connections)
		}
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intVal, err := strconv.Atoi(value); err == nil {
			return intVal
		}
	}
	return defaultValue
}
