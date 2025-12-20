import React, { useState, useContext } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { AuthContext } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Shield, Eye, EyeOff, KeyRound, ArrowLeft } from 'lucide-react';

const AdminLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [twoFactorType, setTwoFactorType] = useState('totp'); // 'totp', 'email', 'sms'
  const { login, API } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const loginData = {
        email,
        password
      };

      // Add verification code if we're in 2FA step
      if (requires2FA) {
        loginData.verification_code = totpCode;
      }

      const response = await axios.post(`${API}/auth/login-enhanced`, loginData);

      const { access_token, user, requires_2fa, two_factor_type, message, code_sent } = response.data;

      // Check if 2FA is required
      if (requires_2fa) {
        setRequires2FA(true);
        setTwoFactorType(two_factor_type || 'totp');

        if (code_sent) {
          toast.success(message || 'Verification code sent!');
        } else {
          toast.info(message || 'Please enter your authentication code');
        }

        setLoading(false);
        return;
      }

      // Successful login
      const adminUser = {
        ...user,
        is_admin: true
      };

      login(adminUser, access_token);
      toast.success('Successfully logged in as admin!');
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed';

      // If 2FA code is invalid, reset the code but stay on 2FA step
      if (requires2FA && errorMessage.includes('2FA')) {
        setTotpCode('');
        toast.error('Invalid authentication code. Please try again.');
      } else {
        toast.error(errorMessage);
        // Reset 2FA state on login failure
        setRequires2FA(false);
        setTotpCode('');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    setRequires2FA(false);
    setTotpCode('');
    setUseBackupCode(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl border-0">
        <CardHeader className="text-center pb-6">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            {requires2FA ? <KeyRound className="w-8 h-8 text-white" /> : <Shield className="w-8 h-8 text-white" />}
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            {requires2FA ? 'Two-Factor Authentication' : 'Admin Portal'}
          </CardTitle>
          <CardDescription className="text-gray-600 mt-2">
            {requires2FA
              ? 'Enter your authentication code to continue'
              : 'Sign in to the admin dashboard'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {requires2FA ? (
            // 2FA Step
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="totpCode" className="text-sm font-medium text-gray-700">
                  {useBackupCode ? 'Backup Code' : 'Authentication Code'}
                </label>
                <Input
                  id="totpCode"
                  type="text"
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, useBackupCode ? 8 : 6))}
                  placeholder={useBackupCode ? 'Enter 8-digit backup code' : 'Enter 6-digit code'}
                  required
                  className="h-11 text-center font-mono text-lg tracking-widest"
                  autoComplete="one-time-code"
                  autoFocus
                />
                <p className="text-xs text-gray-500">
                  {useBackupCode
                    ? 'Enter one of your 8-character backup codes'
                    : twoFactorType === 'email'
                    ? 'Check your email for the 6-digit verification code'
                    : twoFactorType === 'sms'
                    ? 'Check your phone for the 6-digit verification code'
                    : 'Open your authenticator app and enter the 6-digit code'
                  }
                </p>
              </div>

              <div className="space-y-3">
                <Button
                  type="submit"
                  disabled={loading || totpCode.length < (useBackupCode ? 8 : 6)}
                  className="w-full h-11 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold shadow-lg"
                >
                  {loading ? 'Verifying...' : 'Verify & Sign In'}
                </Button>

                <div className="flex flex-col space-y-2">
                  {twoFactorType === 'totp' && (
                    <button
                      type="button"
                      onClick={() => {
                        setUseBackupCode(!useBackupCode);
                        setTotpCode('');
                      }}
                      className="text-sm text-purple-600 hover:text-purple-700 underline"
                    >
                      {useBackupCode ? 'Use authenticator app instead' : 'Use backup code instead'}
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={handleBackToLogin}
                    className="flex items-center justify-center space-x-2 text-sm text-gray-600 hover:text-gray-700"
                  >
                    <ArrowLeft size={16} />
                    <span>Back to login</span>
                  </button>
                </div>
              </div>
            </form>
          ) : (
            // Initial Login Step
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Admin Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your admin email"
                  required
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Admin Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your admin password"
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
              <Button
                type="submit"
                disabled={loading}
                className="w-full h-11 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold shadow-lg"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
          )}

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Admin access only. Unauthorized access is prohibited.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminLogin;