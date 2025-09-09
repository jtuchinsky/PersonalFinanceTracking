import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Edit3, Building } from 'lucide-react';

const EditAccount = () => {
  const [account, setAccount] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    nickname: '',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();
  const { accountId } = useParams();

  useEffect(() => {
    fetchAccount();
  }, [accountId]);

  const fetchAccount = async () => {
    try {
      const response = await axios.get(`${API}/accounts`);
      const foundAccount = response.data.find(acc => acc.id === accountId);
      
      if (!foundAccount) {
        toast.error('Account not found');
        navigate('/manage-accounts');
        return;
      }

      setAccount(foundAccount);
      setFormData({
        name: foundAccount.name || '',
        nickname: foundAccount.nickname || '',
        description: foundAccount.description || ''
      });
    } catch (error) {
      console.error('Failed to fetch account:', error);
      toast.error('Failed to load account');
      navigate('/manage-accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await axios.put(`${API}/accounts/${accountId}`, formData);
      toast.success('Account updated successfully!');
      navigate('/manage-accounts');
    } catch (error) {
      console.error('Account update error:', error);
      toast.error(error.response?.data?.detail || 'Failed to update account');
    } finally {
      setSaving(false);
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

  if (!account) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="text-center py-8">
            <p className="text-gray-600">Account not found</p>
            <Button onClick={() => navigate('/manage-accounts')} className="mt-4">
              Back to Accounts
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/manage-accounts')}
              className="mr-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Accounts
            </Button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <Edit3 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Edit Account</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Update Account Details</CardTitle>
            <div className="bg-gray-50 rounded-lg p-4 mt-4">
              <div className="flex items-center space-x-3">
                <Building className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-semibold text-gray-900">{account.bank_name}</p>
                  <p className="text-sm text-gray-600">
                    {formatAccountType(account.account_type)} • Balance: {formatCurrency(account.balance)}
                  </p>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Account Name */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Account Name</label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="e.g., Chase Freedom, Wells Fargo Checking"
                  required
                  className="h-11"
                />
                <p className="text-xs text-gray-500">Official account name from your bank</p>
              </div>

              {/* Nickname */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Nickname</label>
                <Input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => handleInputChange('nickname', e.target.value)}
                  placeholder="e.g., Primary Card, Emergency Fund"
                  className="h-11"
                />
                <p className="text-xs text-gray-500">Give your account a friendly name (optional)</p>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Description</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="e.g., Main account for daily expenses and bill payments"
                  className="min-h-[100px]"
                />
                <p className="text-xs text-gray-500">Add notes about this account's purpose (optional)</p>
              </div>

              {account.is_default && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> This is a default demo account. You can update the display name and description, 
                    but the core account details cannot be changed.
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex space-x-3 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/manage-accounts')}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={saving}
                  className="flex-1 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold"
                >
                  {saving ? 'Updating...' : 'Update Account'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default EditAccount;