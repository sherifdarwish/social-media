import SubscriptionPlans from "../payments/SubscriptionPlans.jsx"
import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  SettingsIcon,
  Key,
  Link,
  Shield,
  Bell,
  User,
  Save,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  ExternalLink,
  RefreshCw
} from 'lucide-react'

const Settings = () => {
  const [showApiKeys, setShowApiKeys] = useState({})
  const [socialConnections, setSocialConnections] = useState({
    facebook: { connected: false, pages: [] },
    twitter: { connected: false, accounts: [] },
    instagram: { connected: false, accounts: [] },
    linkedin: { connected: false, pages: [] },
    tiktok: { connected: false, accounts: [] }
  })

  const [agentConfigs, setAgentConfigs] = useState({
    facebook: {
      enabled: true,
      postingFrequency: 'daily',
      contentTypes: ['text', 'image', 'video'],
      maxPostsPerDay: 3,
      optimalTimes: ['09:00', '13:00', '18:00']
    },
    twitter: {
      enabled: true,
      postingFrequency: 'multiple',
      contentTypes: ['text', 'image'],
      maxPostsPerDay: 5,
      optimalTimes: ['08:00', '12:00', '15:00', '19:00', '21:00']
    },
    instagram: {
      enabled: true,
      postingFrequency: 'daily',
      contentTypes: ['image', 'video', 'story'],
      maxPostsPerDay: 2,
      optimalTimes: ['11:00', '19:00']
    },
    linkedin: {
      enabled: true,
      postingFrequency: 'weekly',
      contentTypes: ['text', 'image', 'article'],
      maxPostsPerDay: 1,
      optimalTimes: ['09:00']
    },
    tiktok: {
      enabled: false,
      postingFrequency: 'weekly',
      contentTypes: ['video'],
      maxPostsPerDay: 1,
      optimalTimes: ['16:00']
    }
  })

  const [apiKeys, setApiKeys] = useState({
    openai: '',
    claude: '',
    gemini: '',
    midjourney: '',
    stability: '',
    facebook: '',
    twitter: '',
    instagram: '',
    linkedin: '',
    tiktok: ''
  })

  const toggleApiKeyVisibility = (key) => {
    setShowApiKeys(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleSocialConnect = async (platform) => {
    // This would redirect to OAuth flow
    const authUrls = {
      facebook: 'https://www.facebook.com/v18.0/dialog/oauth?client_id=YOUR_APP_ID&redirect_uri=YOUR_REDIRECT_URI&scope=pages_manage_posts,pages_read_engagement',
      twitter: 'https://twitter.com/i/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=tweet.read%20tweet.write%20users.read',
      instagram: 'https://api.instagram.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=user_profile,user_media',
      linkedin: 'https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=w_member_social',
      tiktok: 'https://www.tiktok.com/auth/authorize/?client_key=YOUR_CLIENT_KEY&response_type=code&scope=user.info.basic,video.list'
    }
    
    window.open(authUrls[platform], '_blank', 'width=600,height=600')
  }

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: '📘',
      twitter: '🐦',
      instagram: '📷',
      linkedin: '💼',
      tiktok: '🎵'
    }
    return icons[platform] || '📱'
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-gray-600">Configure your agents and integrations</p>
        </div>
      </div>

      <Tabs defaultValue="agents" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="agents">Agent Configuration</TabsTrigger>
          <TabsTrigger value="social">Social Media</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-6">
          <div className="grid gap-6">
            {Object.entries(agentConfigs).map(([platform, config]) => (
              <Card key={platform}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl">{getPlatformIcon(platform)}</span>
                      {platform.charAt(0).toUpperCase() + platform.slice(1)} Agent
                      <Badge variant={config.enabled ? "default" : "secondary"}>
                        {config.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </CardTitle>
                    <Button
                      variant="outline"
                      onClick={() => setAgentConfigs(prev => ({
                        ...prev,
                        [platform]: { ...prev[platform], enabled: !prev[platform].enabled }
                      }))}
                    >
                      {config.enabled ? "Disable" : "Enable"}
                    </Button>
                  </div>
                  <CardDescription>
                    Configure posting behavior and content preferences for {platform}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Posting Frequency</label>
                      <select 
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={config.postingFrequency}
                        onChange={(e) => setAgentConfigs(prev => ({
                          ...prev,
                          [platform]: { ...prev[platform], postingFrequency: e.target.value }
                        }))}
                      >
                        <option value="multiple">Multiple times daily</option>
                        <option value="daily">Once daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="custom">Custom schedule</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Max Posts Per Day</label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={config.maxPostsPerDay}
                        onChange={(e) => setAgentConfigs(prev => ({
                          ...prev,
                          [platform]: { ...prev[platform], maxPostsPerDay: parseInt(e.target.value) }
                        }))}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Content Types</label>
                    <div className="flex gap-2 flex-wrap">
                      {['text', 'image', 'video', 'story', 'article'].map((type) => (
                        <label key={type} className="flex items-center">
                          <input
                            type="checkbox"
                            className="mr-2"
                            checked={config.contentTypes.includes(type)}
                            onChange={(e) => {
                              const newTypes = e.target.checked
                                ? [...config.contentTypes, type]
                                : config.contentTypes.filter(t => t !== type)
                              setAgentConfigs(prev => ({
                                ...prev,
                                [platform]: { ...prev[platform], contentTypes: newTypes }
                              }))
                            }}
                          />
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Optimal Posting Times</label>
                    <div className="flex gap-2 flex-wrap">
                      {config.optimalTimes.map((time, index) => (
                        <Badge key={index} variant="outline">{time}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="social" className="space-y-6">
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription>
              Connect your social media accounts to enable automated posting. We use OAuth for secure authentication.
            </AlertDescription>
          </Alert>

          <div className="grid gap-6">
            {Object.entries(socialConnections).map(([platform, connection]) => (
              <Card key={platform}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl">{getPlatformIcon(platform)}</span>
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                      {connection.connected ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle size={12} className="mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <XCircle size={12} className="mr-1" />
                          Not Connected
                        </Badge>
                      )}
                    </CardTitle>
                    <Button
                      onClick={() => handleSocialConnect(platform)}
                      variant={connection.connected ? "outline" : "default"}
                    >
                      <ExternalLink size={16} className="mr-2" />
                      {connection.connected ? "Reconnect" : "Connect"}
                    </Button>
                  </div>
                  <CardDescription>
                    {connection.connected 
                      ? `Connected and ready to post. Manage your ${platform} pages and permissions.`
                      : `Connect your ${platform} account to enable automated posting.`
                    }
                  </CardDescription>
                </CardHeader>
                {connection.connected && (
                  <CardContent>
                    <div className="space-y-2">
                      <h4 className="font-medium">Connected Pages/Accounts:</h4>
                      {platform === 'facebook' && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span>My Business Page</span>
                            <Badge variant="outline">Active</Badge>
                          </div>
                        </div>
                      )}
                      {platform === 'linkedin' && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span>Company Page</span>
                            <Badge variant="outline">Active</Badge>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-6">
          <Alert>
            <Key className="h-4 w-4" />
            <AlertDescription>
              Configure API keys for AI services and social media platforms. Keys are encrypted and stored securely.
            </AlertDescription>
          </Alert>

          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>AI Content Generation</CardTitle>
                <CardDescription>API keys for AI-powered content creation</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {['openai', 'claude', 'gemini'].map((service) => (
                  <div key={service} className="flex gap-2">
                    <div className="flex-1">
                      <label className="block text-sm font-medium mb-2">
                        {service.charAt(0).toUpperCase() + service.slice(1)} API Key
                      </label>
                      <div className="relative">
                        <input
                          type={showApiKeys[service] ? "text" : "password"}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md"
                          placeholder={`Enter ${service} API key`}
                          value={apiKeys[service]}
                          onChange={(e) => setApiKeys(prev => ({
                            ...prev,
                            [service]: e.target.value
                          }))}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-1 top-1 h-8 w-8 p-0"
                          onClick={() => toggleApiKeyVisibility(service)}
                        >
                          {showApiKeys[service] ? <EyeOff size={16} /> : <Eye size={16} />}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Image Generation</CardTitle>
                <CardDescription>API keys for AI image generation services</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {['midjourney', 'stability'].map((service) => (
                  <div key={service} className="flex gap-2">
                    <div className="flex-1">
                      <label className="block text-sm font-medium mb-2">
                        {service.charAt(0).toUpperCase() + service.slice(1)} API Key
                      </label>
                      <div className="relative">
                        <input
                          type={showApiKeys[service] ? "text" : "password"}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md"
                          placeholder={`Enter ${service} API key`}
                          value={apiKeys[service]}
                          onChange={(e) => setApiKeys(prev => ({
                            ...prev,
                            [service]: e.target.value
                          }))}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-1 top-1 h-8 w-8 p-0"
                          onClick={() => toggleApiKeyVisibility(service)}
                        >
                          {showApiKeys[service] ? <EyeOff size={16} /> : <Eye size={16} />}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end">
            <Button>
              <Save size={16} className="mr-2" />
              Save API Keys
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="account" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Manage your account settings and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    defaultValue="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input
                    type="email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    defaultValue="john@company.com"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Company</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  defaultValue="My Company"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Choose how you want to be notified</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { id: 'email_reports', label: 'Weekly email reports', checked: true },
                { id: 'post_notifications', label: 'Post publication notifications', checked: true },
                { id: 'error_alerts', label: 'Error and failure alerts', checked: true },
                { id: 'campaign_updates', label: 'Campaign status updates', checked: false }
              ].map((pref) => (
                <label key={pref.id} className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-3"
                    defaultChecked={pref.checked}
                  />
                  {pref.label}
                </label>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Settings

        <TabsContent value="billing" className="space-y-6">
          <SubscriptionPlans currentPlan="free" />
        </TabsContent>
