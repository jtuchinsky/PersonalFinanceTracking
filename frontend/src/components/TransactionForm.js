import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Plus, DollarSign } from 'lucide-react';

const TransactionForm = () => {
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    account_id: '',
    amount: '',
    description: '',
    category: '',
    transaction_type: 'debit',
    date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const { API } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAccounts();
    fetchCategories();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API}/accounts`);
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      toast.error('Failed to load accounts');
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      toast.error('Failed to load categories');
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
    setLoading(true);

    try {
      const transactionData = {
        ...formData,
        amount: parseFloat(formData.amount),
        date: new Date(formData.date + 'T00:00:00Z').toISOString()
      };

      await axios.post(`${API}/transactions`, transactionData);
      toast.success('Transaction added successfully!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Transaction creation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

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
              <h1 className="text-xl font-bold text-gray-900">Add Transaction</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-2xl text-center">New Transaction</CardTitle>
            <p className="text-gray-600 text-center">Add a new income or expense</p>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Transaction Type */}
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => handleInputChange('transaction_type', 'debit')}
                  className={`p-4 rounded-xl border-2 text-center transition-all ${
                    formData.transaction_type === 'debit'
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">Expense</div>
                  <div className="text-sm text-gray-600">Money going out</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleInputChange('transaction_type', 'credit')}
                  className={`p-4 rounded-xl border-2 text-center transition-all ${
                    formData.transaction_type === 'credit'
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">Income</div>
                  <div className="text-sm text-gray-600">Money coming in</div>
                </button>
              </div>

              {/* Amount */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Amount</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => handleInputChange('amount', e.target.value)}
                    placeholder="0.00"
                    required
                    className="pl-10 text-lg h-12"
                  />
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Description</label>
                <Input
                  type="text"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="What was this transaction for?"
                  required
                  className="h-11"
                />
              </div>

              {/* Account */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Account</label>
                <Select 
                  value={formData.account_id} 
                  onValueChange={(value) => handleInputChange('account_id', value)}
                >
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select account" />
                  </SelectTrigger>
                  <SelectContent>
                    {accounts.map((account) => (
                      <SelectItem key={account.id} value={account.id}>
                        <div className="flex items-center space-x-2">
                          <span>{account.name}</span>
                          <span className="text-gray-500">({account.bank_name})</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Category */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Category</label>
                <Select 
                  value={formData.category} 
                  onValueChange={(value) => handleInputChange('category', value)}
                >
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.name}>
                        <div className="flex items-center space-x-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: category.color }}
                          ></div>
                          <span>{category.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Date */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Date</label>
                <Input
                  type="date"
                  value={formData.date}
                  onChange={(e) => handleInputChange('date', e.target.value)}
                  required
                  className="h-11"
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold text-lg"
              >
                {loading ? 'Adding Transaction...' : 'Add Transaction'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default TransactionForm;