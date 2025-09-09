import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Edit3,
  Wallet,
  PiggyBank,
  CreditCard,
  Building,
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
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

const AccountManager = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, account: null });
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API}/accounts`);
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      toast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (account) => {
    try {
      await axios.delete(`${API}/accounts/${account.id}`);
      toast.success('Account deleted successfully!');
      setAccounts(accounts.filter(acc => acc.id !== account.id));
      setDeleteDialog({ open: false, account: null });
    } catch (error) {
      console.error('Delete account error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to delete account';
      toast.error(errorMessage);
    }
  };

  const getAccountIcon = (type) => {
    switch (type) {
      case 'checking':
        return <Wallet className="w-6 h-6" />;
      case 'savings':
        return <PiggyBank className="w-6 h-6" />;
      case 'credit_card':
        return <CreditCard className="w-6 h-6" />;
      default:
        return <Building className="w-6 h-6" />;
    }
  };

  const getAccountColor = (type) => {
    switch (type) {
      case 'checking':
        return 'from-emerald-500 to-emerald-600';
      case 'savings':
        return 'from-blue-500 to-blue-600';
      case 'credit_card':
        return 'from-amber-500 to-amber-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatAccountType = (type) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
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
              <h1 className="text-xl font-bold text-gray-900">Manage Accounts</h1>
            </div>
            <Link to="/add-account">
              <Button className="bg-emerald-600 hover:bg-emerald-700">
                <Plus className="w-4 h-4 mr-2" />
                Add Account
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Accounts</h2>
          <p className="text-gray-600">Manage your banking and credit card accounts</p>
        </div>

        {accounts.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Building className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No accounts yet</h3>
              <p className="text-gray-600 mb-6">Add your first banking or credit card account to get started</p>
              <Link to="/add-account">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Account
                </Button>
              </Link>  
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {accounts.map((account) => (
              <Card key={account.id} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-12 h-12 bg-gradient-to-br ${getAccountColor(account.account_type)} rounded-xl flex items-center justify-center text-white`}>
                        {getAccountIcon(account.account_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-lg truncate">
                          {account.nickname || account.name}
                        </CardTitle>
                        <p className="text-sm text-gray-600">
                          {account.bank_name} • {formatAccountType(account.account_type)}
                        </p>
                        {account.nickname && account.nickname !== account.name && (
                          <p className="text-xs text-gray-500 truncate">{account.name}</p>
                        )}
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => navigate(`/edit-account/${account.id}`)}>
                          <Edit3 className="w-4 h-4 mr-2" />
                          Edit Account
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => setDeleteDialog({ open: true, account })}
                          className="text-red-600 focus:text-red-600"
                          disabled={account.is_default}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete Account
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${account.balance >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {formatCurrency(account.balance)}
                      </p>
                    </div>
                    
                    {account.description && (
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-700">{account.description}</p>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Added {new Date(account.created_at).toLocaleDateString()}</span>
                      {account.is_default && (
                        <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                          Default Account
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, account: deleteDialog.account })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Account</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteDialog.account?.nickname || deleteDialog.account?.name}"? 
              This action cannot be undone. You must delete all transactions associated with this account first.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => handleDeleteAccount(deleteDialog.account)}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Account
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AccountManager;