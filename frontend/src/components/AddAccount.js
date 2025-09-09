import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Plus, Building, CreditCard, PiggyBank, Wallet, Eye, EyeOff } from 'lucide-react';

const AddAccount = () => {
  const [formData, setFormData] = useState({
    name: '',
    account_type: '',
    bank_name: '',
    nickname: '',
    description: '',
    account_username: '',
    account_password: '',
    initial_balance: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const accountData = {
        ...formData,
        initial_balance: parseFloat(formData.initial_balance) || 0.0
      };

      await axios.post(`${API}/accounts`, accountData);
      toast.success('Account added successfully!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Account creation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to add account');
    } finally {
      setLoading(false);
    }
  };

  const getAccountTypeIcon = (type) => {
    switch (type) {
      case 'checking':
        return <Wallet className="w-5 h-5" />;
      case 'savings':
        return <PiggyBank className="w-5 h-5" />;
      case 'credit_card':
        return <CreditCard className="w-5 h-5" />;
      default:
        return <Building className="w-5 h-5" />;
    }
  };

  const bankOptions = [
    'TD Bank', 'Chase', 'Bank of America', 'Wells Fargo', 'Citibank',
    'Capital One', 'US Bank', 'PNC Bank', 'Truist', 'Fifth Third Bank',
    'Ally Bank', 'Discover Bank', 'American Express', 'Other'
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className="mr-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <Plus className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Add Banking Account</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Connect Your Account</CardTitle>
            <p className="text-gray-600 text-center">Add a banking or credit card account to track your finances</p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> This is a demo app. Your credentials are encrypted and stored securely, 
                but no actual bank connections are made.
              </p>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Account Type Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-gray-700">Account Type</label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => handleInputChange('account_type', 'checking')}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      formData.account_type === 'checking'
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Wallet className="w-6 h-6 mx-auto mb-2" />
                    <div className="font-semibold">Checking</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('account_type', 'savings')}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      formData.account_type === 'savings'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <PiggyBank className="w-6 h-6 mx-auto mb-2" />
                    <div className="font-semibold">Savings</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('account_type', 'credit_card')}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      formData.account_type === 'credit_card'
                        ? 'border-amber-500 bg-amber-50 text-amber-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <CreditCard className="w-6 h-6 mx-auto mb-2" />
                    <div className="font-semibold">Credit Card</div>
                  </button>
                </div>
              </div>

              {/* Bank Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Bank/Institution</label>
                <Select 
                  value={formData.bank_name} 
                  onValueChange={(value) => handleInputChange('bank_name', value)}
                >
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select your bank" />
                  </SelectTrigger>
                  <SelectContent>
                    {bankOptions.map((bank) => (
                      <SelectItem key={bank} value={bank}>
                        {bank}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

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
              </div>

              {/* Nickname */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Nickname (Optional)</label>
                <Input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => handleInputChange('nickname', e.target.value)}
                  placeholder="e.g., Primary Card, Emergency Fund"
                  className="h-11"
                />
                <p className="text-xs text-gray-500">Give your account a friendly name</p>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Description (Optional)</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="e.g., Main account for daily expenses and bill payments"
                  className="min-h-[80px]"
                />
              </div>

              {/* Login Credentials */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center">
                  <Building className="w-5 h-5 mr-2" />
                  Banking Credentials
                </h3>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Username/Email</label>
                  <Input
                    type="text"
                    value={formData.account_username}
                    onChange={(e) => handleInputChange('account_username', e.target.value)}
                    placeholder="Your banking username or email"
                    required
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Password</label>
                  <div className="relative">
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.account_password}
                      onChange={(e) => handleInputChange('account_password', e.target.value)}
                      placeholder="Your banking password"
                      required
                      className="h-11 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Initial Balance */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Current Balance {formData.account_type === 'credit_card' ? '(Amount Owed)' : ''}
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.initial_balance}
                    onChange={(e) => handleInputChange('initial_balance', e.target.value)}
                    placeholder="0.00"
                    className="pl-8 h-11"
                  />
                </div>
                {formData.account_type === 'credit_card' && (
                  <p className="text-xs text-gray-500">Enter amount owed (will be shown as negative balance)</p>
                )}
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold text-lg"
              >
                {loading ? 'Adding Account...' : 'Add Account'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default AddAccount;