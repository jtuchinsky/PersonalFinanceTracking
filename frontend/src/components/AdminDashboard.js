import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  Users, 
  Shield, 
  Activity, 
  DollarSign,
  Lock,
  Unlock,
  Trash2,
  Mail,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [sentEmails, setSentEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [actionDialog, setActionDialog] = useState({ open: false, type: '', user: null });
  const { user, logout, API } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is admin
    if (!user?.is_admin) {
      toast.error('Admin access required');
      navigate('/dashboard');
      return;
    }
    
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes, activitiesRes, emailsRes] = await Promise.all([
        axios.get(`${API}/admin/stats`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/activities`),
        axios.get(`${API}/admin/emails`)
      ]);
      
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setActivities(activitiesRes.data);
      setSentEmails(emailsRes.data.sent_emails);
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (action, userId) => {
    try {
      let response;
      
      switch (action) {
        case 'lock':
          response = await axios.post(`${API}/admin/users/${userId}/lock`);
          break;
        case 'unlock':
          response = await axios.post(`${API}/admin/users/${userId}/unlock`);
          break;
        case 'delete':
          response = await axios.delete(`${API}/admin/users/${userId}`);
          break;
        default:
          return;
      }
      
      toast.success(response.data.message);
      setActionDialog({ open: false, type: '', user: null });
      await fetchData(); // Refresh data
      
    } catch (error) {
      console.error(`Failed to ${action} user:`, error);
      toast.error(error.response?.data?.detail || `Failed to ${action} user`);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'locked':
        return <Badge className="bg-red-100 text-red-800">Locked</Badge>;
      case 'deleted':
        return <Badge className="bg-gray-100 text-gray-800">Deleted</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">Unknown</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-emerald-600" />
                <h1 className="text-xl font-bold text-gray-900">Admin Panel</h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">Welcome, {user?.name}</span>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex space-x-4 mb-6">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'outline'}
            onClick={() => setActiveTab('overview')}
            className={activeTab === 'overview' ? 'bg-emerald-600' : ''}
          >
            <Activity className="w-4 h-4 mr-2" />
            Overview
          </Button>
          <Button
            variant={activeTab === 'users' ? 'default' : 'outline'}
            onClick={() => setActiveTab('users')}
            className={activeTab === 'users' ? 'bg-emerald-600' : ''}
          >
            <Users className="w-4 h-4 mr-2" />
            User Management
          </Button>
          <Button
            variant={activeTab === 'activities' ? 'default' : 'outline'}
            onClick={() => setActiveTab('activities')}
            className={activeTab === 'activities' ? 'bg-emerald-600' : ''}
          >
            <Clock className="w-4 h-4 mr-2" />
            Activity Logs
          </Button>
          <Button
            variant={activeTab === 'emails' ? 'default' : 'outline'}
            onClick={() => setActiveTab('emails')}
            className={activeTab === 'emails' ? 'bg-emerald-600' : ''}
          >
            <Mail className="w-4 h-4 mr-2" />
            Email Logs
          </Button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Users</p>
                      <p className="text-3xl font-bold text-gray-900">{stats?.total_users || 0}</p>
                    </div>
                    <Users className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Active Users</p>
                      <p className="text-3xl font-bold text-green-600">{stats?.active_users || 0}</p>
                    </div>
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Locked Users</p>
                      <p className="text-3xl font-bold text-red-600">{stats?.locked_users || 0}</p>
                    </div>
                    <Lock className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Accounts</p>
                      <p className="text-3xl font-bold text-purple-600">{stats?.total_accounts || 0}</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activities */}
            <Card>
              <CardHeader>
                <CardTitle>Recent System Activities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {stats?.recent_activities?.slice(0, 10).map((activity) => (
                    <div key={activity.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                      <Activity className="w-5 h-5 text-gray-500" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{activity.action}</p>
                        <p className="text-sm text-gray-600">{activity.details}</p>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(activity.timestamp)}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <p className="text-sm text-gray-600">Manage user accounts, lock/unlock, and delete users</p>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">User</th>
                      <th className="text-left py-3 px-4">Status</th>
                      <th className="text-left py-3 px-4">Accounts</th>
                      <th className="text-left py-3 px-4">Balance</th>
                      <th className="text-left py-3 px-4">Last Login</th>
                      <th className="text-left py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-gray-600">{user.email}</p>
                            {user.is_admin && (
                              <Badge className="bg-purple-100 text-purple-800 text-xs mt-1">
                                Admin
                              </Badge>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {getStatusBadge(user.account_status)}
                        </td>
                        <td className="py-3 px-4">
                          <div className="text-sm">
                            <p>{user.total_accounts} accounts</p>
                            <p className="text-gray-600">{user.total_transactions} transactions</p>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`font-medium ${user.total_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(user.total_balance)}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm text-gray-600">
                            {user.last_login ? formatDate(user.last_login) : 'Never'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          {!user.is_admin && (
                            <div className="flex space-x-2">
                              {user.account_status === 'active' ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setActionDialog({ open: true, type: 'lock', user })}
                                >
                                  <Lock className="w-4 h-4 mr-1" />
                                  Lock
                                </Button>
                              ) : (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setActionDialog({ open: true, type: 'unlock', user })}
                                >
                                  <Unlock className="w-4 h-4 mr-1" />
                                  Unlock
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setActionDialog({ open: true, type: 'delete', user })}
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="w-4 h-4 mr-1" />
                                Delete
                              </Button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Activities Tab */}
        {activeTab === 'activities' && (
          <Card>
            <CardHeader>
              <CardTitle>System Activity Logs</CardTitle>
              <p className="text-sm text-gray-600">Monitor user and admin activities</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      {activity.action.includes('admin') ? (
                        <Shield className="w-5 h-5 text-purple-600 mt-0.5" />
                      ) : activity.action.includes('login') ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      ) : activity.action.includes('lock') || activity.action.includes('delete') ? (
                        <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                      ) : (
                        <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-gray-900">{activity.action}</p>
                        <span className="text-xs text-gray-500">{formatDate(activity.timestamp)}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{activity.details}</p>
                      {activity.ip_address && (
                        <p className="text-xs text-gray-500 mt-1">IP: {activity.ip_address}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Emails Tab */}
        {activeTab === 'emails' && (
          <Card>
            <CardHeader>
              <CardTitle>Email Notification Logs</CardTitle>
              <p className="text-sm text-gray-600">View all sent email notifications</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sentEmails.map((email) => (
                  <div key={email.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Mail className="w-4 h-4 text-blue-600" />
                        <span className="font-medium">{email.subject}</span>
                        <Badge className={`text-xs ${
                          email.type === 'account_deleted' ? 'bg-red-100 text-red-800' :
                          email.type === 'account_locked' ? 'bg-yellow-100 text-yellow-800' :
                          email.type === 'account_unlocked' ? 'bg-green-100 text-green-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {email.type}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">{formatDate(email.sent_at)}</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">To: {email.to}</p>
                    <div className="bg-white p-3 rounded border text-sm">
                      <pre className="whitespace-pre-wrap font-sans">{email.body}</pre>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Action Confirmation Dialog */}
      <AlertDialog open={actionDialog.open} onOpenChange={(open) => setActionDialog({ ...actionDialog, open })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {actionDialog.type === 'lock' && 'Lock User Account'}
              {actionDialog.type === 'unlock' && 'Unlock User Account'}
              {actionDialog.type === 'delete' && 'Delete User Account'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {actionDialog.type === 'lock' && (
                <>Are you sure you want to lock the account for <strong>{actionDialog.user?.name}</strong>? 
                The user will not be able to log in until unlocked. An email notification will be sent.</>
              )}
              {actionDialog.type === 'unlock' && (
                <>Are you sure you want to unlock the account for <strong>{actionDialog.user?.name}</strong>? 
                The user will be able to log in normally. An email notification will be sent.</>
              )}
              {actionDialog.type === 'delete' && (
                <>Are you sure you want to delete the account for <strong>{actionDialog.user?.name}</strong>? 
                This action cannot be undone. All user data will be permanently removed and an email notification will be sent.</>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => handleUserAction(actionDialog.type, actionDialog.user?.id)}
              className={`${
                actionDialog.type === 'delete' 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : actionDialog.type === 'lock'
                  ? 'bg-yellow-600 hover:bg-yellow-700'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {actionDialog.type === 'lock' && 'Lock Account'}
              {actionDialog.type === 'unlock' && 'Unlock Account'}
              {actionDialog.type === 'delete' && 'Delete Account'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AdminDashboard;