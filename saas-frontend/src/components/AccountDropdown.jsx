import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { 
  Settings, 
  User, 
  CreditCard, 
  LogOut, 
  Shield, 
  HelpCircle,
  Crown,
  Building2
} from 'lucide-react'

const AccountDropdown = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    // Implement logout logic
    console.log('Logging out...')
    setIsOpen(false)
  }

  const menuItems = [
    {
      icon: <User className="h-4 w-4" />,
      label: 'Profile Settings',
      description: 'Manage your personal information',
      action: () => console.log('Profile settings')
    },
    {
      icon: <Building2 className="h-4 w-4" />,
      label: 'Organization',
      description: 'Manage team and organization settings',
      action: () => console.log('Organization settings')
    },
    {
      icon: <CreditCard className="h-4 w-4" />,
      label: 'Billing & Subscription',
      description: 'View billing history and manage subscription',
      action: () => console.log('Billing settings')
    },
    {
      icon: <Shield className="h-4 w-4" />,
      label: 'Security',
      description: 'Password, 2FA, and security settings',
      action: () => console.log('Security settings')
    },
    {
      icon: <HelpCircle className="h-4 w-4" />,
      label: 'Help & Support',
      description: 'Get help and contact support',
      action: () => console.log('Help & Support')
    }
  ]

  return (
    <div className="relative" ref={dropdownRef}>
      <Button 
        variant="outline" 
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2"
      >
        <Settings size={16} />
        <span>Account</span>
      </Button>

      {isOpen && (
        <Card className="absolute right-0 top-full mt-2 w-72 z-50 shadow-lg">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-sm font-medium">{user?.name || 'John Doe'}</CardTitle>
                <CardDescription className="text-xs">{user?.email || 'john@example.com'}</CardDescription>
              </div>
            </div>
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center space-x-2">
                <Badge variant={user?.tenant?.plan === 'pro' ? 'default' : 'secondary'} className="text-xs">
                  {user?.tenant?.plan === 'pro' && <Crown className="h-3 w-3 mr-1" />}
                  {user?.tenant?.plan || 'Free'} Plan
                </Badge>
              </div>
              <div className="text-xs text-gray-500">
                {user?.tenant?.name || 'Personal'}
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            <div className="space-y-1">
              {menuItems.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    item.action()
                    setIsOpen(false)
                  }}
                  className="w-full text-left p-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start space-x-3">
                    <div className="mt-0.5 text-gray-600">
                      {item.icon}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">
                        {item.label}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {item.description}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            
            <Separator className="my-2" />
            
            <button
              onClick={handleLogout}
              className="w-full text-left p-3 hover:bg-red-50 transition-colors text-red-600"
            >
              <div className="flex items-center space-x-3">
                <LogOut className="h-4 w-4" />
                <span className="text-sm font-medium">Sign Out</span>
              </div>
            </button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default AccountDropdown
