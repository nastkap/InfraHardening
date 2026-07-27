import React from 'react';
import { 
  Users, 
  Server, 
  CreditCard, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

export function Dashboard() {
  const stats = [
    {
      name: 'Total Customers',
      value: '24',
      change: '+12%',
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      name: 'Active VMs',
      value: '156',
      change: '+8%',
      icon: Server,
      color: 'bg-green-500'
    },
    {
      name: 'Monthly Revenue',
      value: 'PLN 45,000',
      change: '+15%',
      icon: CreditCard,
      color: 'bg-purple-500'
    },
    {
      name: 'Growth Rate',
      value: '+23%',
      change: '+5%',
      icon: TrendingUp,
      color: 'bg-orange-500'
    }
  ];

  const recentActivity = [
    {
      customer: 'Acme Corporation',
      action: 'Infrastructure provisioned',
      time: '2 hours ago',
      status: 'completed'
    },
    {
      customer: 'TechStart Ltd',
      action: 'Subscription upgraded',
      time: '4 hours ago',
      status: 'completed'
    },
    {
      customer: 'Global Industries',
      action: 'Security scan completed',
      time: '6 hours ago',
      status: 'completed'
    },
    {
      customer: 'StartupXYZ',
      action: 'Payment received',
      time: '8 hours ago',
      status: 'completed'
    },
    {
      customer: 'MediaGroup',
      action: 'Support ticket created',
      time: '12 hours ago',
      status: 'pending'
    }
  ];

  const alerts = [
    {
      type: 'warning',
      message: 'Customer ABC Corp has 85% VM usage',
      time: '1 hour ago'
    },
    {
      type: 'error',
      message: 'Payment failed for customer XYZ Ltd',
      time: '3 hours ago'
    },
    {
      type: 'info',
      message: 'New customer signup: Startup Inc',
      time: '5 hours ago'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Overview of your infrastructure business</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="p-6 bg-white rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
            <div className="mt-4">
              <span className="text-sm font-medium text-green-600">{stat.change}</span>
              <span className="text-sm text-gray-500"> from last month</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Revenue Chart Placeholder */}
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900">Revenue Overview</h3>
          <div className="mt-4 h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">Revenue chart will be displayed here</p>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          <div className="mt-4 space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0">
                  {activity.status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <Clock className="w-5 h-5 text-yellow-500" />
                  )}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">{activity.customer}</p>
                  <p className="text-sm text-gray-500">{activity.action}</p>
                  <p className="text-xs text-gray-400">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts */}
      <div className="p-6 bg-white rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900">Alerts & Notifications</h3>
        <div className="mt-4 space-y-3">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`flex items-start p-4 rounded-lg ${
                alert.type === 'error' ? 'bg-red-50' :
                alert.type === 'warning' ? 'bg-yellow-50' : 'bg-blue-50'
              }`}
            >
              <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                alert.type === 'error' ? 'text-red-500' :
                alert.type === 'warning' ? 'text-yellow-500' : 'text-blue-500'
              }`} />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-6 bg-white rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <button className="flex items-center justify-center px-4 py-3 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
            Add New Customer
          </button>
          <button className="flex items-center justify-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            Run Security Scan
          </button>
          <button className="flex items-center justify-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            Generate Report
          </button>
        </div>
      </div>
    </div>
  );
}
