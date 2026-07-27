import React from 'react';
import { Settings as SettingsIcon, Bell, Shield, CreditCard, Users, Database } from 'lucide-react';

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">Configure your platform settings</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Settings Navigation */}
        <div className="space-y-2">
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-white bg-indigo-600 rounded-lg">
            <SettingsIcon className="w-5 h-5 mr-3" />
            General
          </button>
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <Bell className="w-5 h-5 mr-3" />
            Notifications
          </button>
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <Shield className="w-5 h-5 mr-3" />
            Security
          </button>
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <CreditCard className="w-5 h-5 mr-3" />
            Billing
          </button>
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <Users className="w-5 h-5 mr-3" />
            Users
          </button>
          <button className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <Database className="w-5 h-5 mr-3" />
            Integrations
          </button>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* General Settings */}
          <div className="p-6 bg-white rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">General Settings</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Company Name</label>
                <input
                  type="text"
                  defaultValue="InfraHardening Ltd"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Contact Email</label>
                <input
                  type="email"
                  defaultValue="admin@infrahardening.com"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Default Currency</label>
                <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>PLN - Polish Zloty</option>
                  <option>EUR - Euro</option>
                  <option>USD - US Dollar</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Timezone</label>
                <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>Europe/Warsaw</option>
                  <option>Europe/London</option>
                  <option>America/New_York</option>
                </select>
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>

          {/* Notification Settings */}
          <div className="p-6 bg-white rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Email Notifications</p>
                  <p className="text-sm text-gray-500">Receive email alerts for important events</p>
                </div>
                <input type="checkbox" defaultChecked className="w-4 h-4 text-indigo-600 rounded" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Slack Notifications</p>
                  <p className="text-sm text-gray-500">Send alerts to Slack channel</p>
                </div>
                <input type="checkbox" defaultChecked className="w-4 h-4 text-indigo-600 rounded" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">SMS Alerts</p>
                  <p className="text-sm text-gray-500">Critical alerts via SMS</p>
                </div>
                <input type="checkbox" className="w-4 h-4 text-indigo-600 rounded" />
              </div>
            </div>
          </div>

          {/* Security Settings */}
          <div className="p-6 bg-white rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Two-Factor Authentication</label>
                <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>Disabled</option>
                  <option>SMS</option>
                  <option>Authenticator App</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Session Timeout</label>
                <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>30 minutes</option>
                  <option>1 hour</option>
                  <option>4 hours</option>
                  <option>24 hours</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">IP Whitelist</p>
                  <p className="text-sm text-gray-500">Restrict access to specific IPs</p>
                </div>
                <input type="checkbox" className="w-4 h-4 text-indigo-600 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
