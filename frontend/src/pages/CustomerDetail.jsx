import React from 'react';
import { useParams } from 'react-router-dom';
import { ArrowLeft, Server, CreditCard, FileText, AlertTriangle } from 'lucide-react';

export function CustomerDetail() {
  const { id } = useParams();

  // Mock customer data
  const customer = {
    id: id,
    name: 'Acme Corporation',
    contact: 'John Smith',
    email: 'john@acme.com',
    phone: '+48 123 456 789',
    address: '123 Business Street, Warsaw, Poland',
    plan: 'Pro',
    status: 'active',
    startDate: '2024-01-15',
    vms: 8,
    monthlyCost: 1500,
    uptime: '99.8%'
  };

  const infrastructure = [
    { id: 1, name: 'acme-web-01', type: 'VM', status: 'running', location: 'West Europe' },
    { id: 2, name: 'acme-web-02', type: 'VM', status: 'running', location: 'West Europe' },
    { id: 3, name: 'acme-app-01', type: 'VM', status: 'running', location: 'West Europe' },
    { id: 4, name: 'acme-db-01', type: 'VM', status: 'running', location: 'West Europe' },
  ];

  const recentInvoices = [
    { id: 'INV-2024-001', amount: 1500, status: 'paid', date: '2024-01-15' },
    { id: 'INV-2024-002', amount: 1500, status: 'paid', date: '2024-02-15' },
    { id: 'INV-2024-003', amount: 1500, status: 'pending', date: '2024-03-15' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <button className="mr-4 text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
          <p className="mt-1 text-sm text-gray-500">Customer Details</p>
        </div>
      </div>

      {/* Customer Info */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-500">Contact Person</p>
              <p className="text-sm text-gray-900">{customer.contact}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Email</p>
              <p className="text-sm text-gray-900">{customer.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Phone</p>
              <p className="text-sm text-gray-900">{customer.phone}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Address</p>
              <p className="text-sm text-gray-900">{customer.address}</p>
            </div>
          </div>
        </div>

        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Subscription</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-500">Plan</p>
              <p className="text-sm text-gray-900">{customer.plan}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                {customer.status}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Start Date</p>
              <p className="text-sm text-gray-900">{customer.startDate}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Monthly Cost</p>
              <p className="text-sm text-gray-900">PLN {customer.monthlyCost.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Infrastructure</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-500">Total VMs</p>
              <p className="text-sm text-gray-900">{customer.vms}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Uptime</p>
              <p className="text-sm text-gray-900">{customer.uptime}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Security Status</p>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                Secure
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Infrastructure */}
      <div className="p-6 bg-white rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Infrastructure Resources</h3>
          <button className="text-sm text-indigo-600 hover:text-indigo-700">
            View All
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {infrastructure.map((resource) => (
                <tr key={resource.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {resource.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {resource.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      {resource.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {resource.location}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Invoices */}
      <div className="p-6 bg-white rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Invoices</h3>
          <button className="text-sm text-indigo-600 hover:text-indigo-700">
            View All
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentInvoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {invoice.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    PLN {invoice.amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      invoice.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {invoice.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {invoice.date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
