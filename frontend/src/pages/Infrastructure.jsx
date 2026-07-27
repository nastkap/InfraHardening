import React from 'react';
import { Server, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export function Infrastructure() {
  const resources = [
    {
      id: 1,
      customer: 'Acme Corporation',
      resource: 'acme-web-01',
      type: 'VM',
      status: 'running',
      location: 'West Europe',
      cpu: '45%',
      memory: '62%',
      uptime: '99.9%'
    },
    {
      id: 2,
      customer: 'Acme Corporation',
      resource: 'acme-web-02',
      type: 'VM',
      status: 'running',
      location: 'West Europe',
      cpu: '38%',
      memory: '55%',
      uptime: '99.8%'
    },
    {
      id: 3,
      customer: 'TechStart Ltd',
      resource: 'techstart-app-01',
      type: 'VM',
      status: 'running',
      location: 'West Europe',
      cpu: '72%',
      memory: '78%',
      uptime: '99.5%'
    },
    {
      id: 4,
      customer: 'Global Industries',
      resource: 'global-db-01',
      type: 'VM',
      status: 'running',
      location: 'West Europe',
      cpu: '25%',
      memory: '45%',
      uptime: '99.9%'
    },
    {
      id: 5,
      customer: 'StartupXYZ',
      resource: 'startup-web-01',
      type: 'VM',
      status: 'stopped',
      location: 'West Europe',
      cpu: '0%',
      memory: '0%',
      uptime: '98.5%'
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'stopped':
        return <Clock className="w-5 h-5 text-gray-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'running': 'bg-green-100 text-green-800',
      'stopped': 'bg-gray-100 text-gray-800',
      'error': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors['stopped'];
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Infrastructure</h1>
        <p className="mt-1 text-sm text-gray-500">Monitor and manage all infrastructure resources</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Server className="w-8 h-8 text-indigo-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Resources</p>
              <p className="text-2xl font-bold text-gray-900">156</p>
            </div>
          </div>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Running</p>
              <p className="text-2xl font-bold text-gray-900">142</p>
            </div>
          </div>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-gray-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Stopped</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <div className="flex items-center">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Issues</p>
              <p className="text-2xl font-bold text-gray-900">2</p>
            </div>
          </div>
        </div>
      </div>

      {/* Resources Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Resource
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                CPU
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Memory
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Uptime
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {resources.map((resource) => (
              <tr key={resource.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {getStatusIcon(resource.status)}
                    <span className="ml-2 text-sm font-medium text-gray-900">{resource.resource}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {resource.customer}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {resource.type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(resource.status)}`}>
                    {resource.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {resource.location}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {resource.cpu}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {resource.memory}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {resource.uptime}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
