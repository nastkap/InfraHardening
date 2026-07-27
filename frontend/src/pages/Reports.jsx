import React from 'react';
import { FileText, Download, Calendar, BarChart3 } from 'lucide-react';

export function Reports() {
  const reports = [
    {
      id: 1,
      name: 'Monthly Security Report',
      type: 'security',
      customer: 'Acme Corporation',
      period: 'March 2024',
      status: 'completed',
      createdAt: '2024-03-31'
    },
    {
      id: 2,
      name: 'Infrastructure Usage Report',
      type: 'usage',
      customer: 'Global Industries',
      period: 'March 2024',
      status: 'completed',
      createdAt: '2024-03-31'
    },
    {
      id: 3,
      name: 'Cost Analysis Report',
      type: 'cost',
      customer: 'TechStart Ltd',
      period: 'Q1 2024',
      status: 'generating',
      createdAt: '2024-04-01'
    },
    {
      id: 4,
      name: 'Performance Report',
      type: 'performance',
      customer: 'MediaGroup',
      period: 'March 2024',
      status: 'completed',
      createdAt: '2024-03-30'
    }
  ];

  const getReportTypeBadge = (type) => {
    const colors = {
      'security': 'bg-red-100 text-red-800',
      'usage': 'bg-blue-100 text-blue-800',
      'cost': 'bg-green-100 text-green-800',
      'performance': 'bg-purple-100 text-purple-800'
    };
    return colors[type] || colors['usage'];
  };

  const getStatusBadge = (status) => {
    const colors = {
      'completed': 'bg-green-100 text-green-800',
      'generating': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors['generating'];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-1 text-sm text-gray-500">Generate and download reports</p>
        </div>
        <button className="flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
          <FileText className="w-4 h-4 mr-2" />
          Generate Report
        </button>
      </div>

      {/* Report Types */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <button className="p-6 bg-white rounded-lg shadow-sm border hover:border-indigo-500 transition-colors">
          <BarChart3 className="w-8 h-8 text-indigo-600 mb-3" />
          <h3 className="text-sm font-medium text-gray-900">Security Report</h3>
          <p className="text-xs text-gray-500 mt-1">Vulnerability scan results</p>
        </button>
        <button className="p-6 bg-white rounded-lg shadow-sm border hover:border-indigo-500 transition-colors">
          <BarChart3 className="w-8 h-8 text-green-600 mb-3" />
          <h3 className="text-sm font-medium text-gray-900">Usage Report</h3>
          <p className="text-xs text-gray-500 mt-1">Resource utilization metrics</p>
        </button>
        <button className="p-6 bg-white rounded-lg shadow-sm border hover:border-indigo-500 transition-colors">
          <BarChart3 className="w-8 h-8 text-blue-600 mb-3" />
          <h3 className="text-sm font-medium text-gray-900">Cost Report</h3>
          <p className="text-xs text-gray-500 mt-1">Billing and cost analysis</p>
        </button>
        <button className="p-6 bg-white rounded-lg shadow-sm border hover:border-indigo-500 transition-colors">
          <BarChart3 className="w-8 h-8 text-purple-600 mb-3" />
          <h3 className="text-sm font-medium text-gray-900">Performance Report</h3>
          <p className="text-xs text-gray-500 mt-1">System performance metrics</p>
        </button>
      </div>

      {/* Reports Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-medium text-gray-900">Recent Reports</h3>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Report Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Period
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {reports.map((report) => (
              <tr key={report.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {report.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getReportTypeBadge(report.type)}`}>
                    {report.type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {report.customer}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {report.period}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(report.status)}`}>
                    {report.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {report.createdAt}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button 
                    className="text-indigo-600 hover:text-indigo-700 disabled:text-gray-400"
                    disabled={report.status !== 'completed'}
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
