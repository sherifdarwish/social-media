import CampaignsPage from "./components/CampaignsPage.jsx"
import AnalyticsPage from "./components/AnalyticsPage.jsx"
import EnhancedContentApproval from "./components/EnhancedContentApproval.jsx"
import EnhancedGeneratorInterface from "./components/EnhancedGeneratorInterface.jsx"
import NotificationDropdown from "./components/NotificationDropdown.jsx"
import AccountDropdown from "./components/AccountDropdown.jsx"
import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Building2, 
  Users, 
  BarChart3, 
  Settings, 
  PlusCircle, 
  Target, 
  Lightbulb,
  Calendar,
  TrendingUp,
  MessageSquare,
  Heart,
  Share2,
  Eye,
  CheckCircle,
  XCircle,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Trash2,
  Download,
  Upload,
  Bell,
  Search,
  Filter,
  MoreHorizontal
} from 'lucide-react'
import './App.css'

// Mock authentication state
const useAuth = () => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate authentication check
    setTimeout(() => {
      setUser({
        id: '1',
        email: 'admin@company.com',
        name: 'John Doe',
        role: 'admin',
        tenant: {
          id: 'tenant-1',
          name: 'Acme Corporation',
          plan: 'premium'
        }
      })
      setLoading(false)
    }, 1000)
  }, [])

  return { user, loading, setUser }
}

// Mock data
const mockBusinessProfiles = [
  {
    id: '1',
    company_name: 'Acme Corporation',
    industry: 'Technology',
    target_audience: 'Business professionals',
    brand_voice: 'Professional and innovative',
    created_at: '2024-01-15'
  }
]

const mockContentSuggestions = [
  {
    id: '1',
    platform: 'linkedin',
    content_type: 'educational',
    title: 'The Future of AI in Business',
    content: 'Artificial Intelligence is transforming how businesses operate. Here are 5 key trends every leader should know about AI implementation in 2024...',
    hashtags: ['#AI', '#Business', '#Technology', '#Innovation'],
    engagement_prediction: 85,
    status: 'pending',
    created_at: '2024-01-20T10:00:00Z'
  },
  {
    id: '2',
    platform: 'twitter',
    content_type: 'promotional',
    title: 'New Product Launch',
    content: '🚀 Excited to announce our latest innovation! Our new AI-powered solution is helping businesses increase efficiency by 40%. Ready to transform your workflow?',
    hashtags: ['#ProductLaunch', '#AI', '#Efficiency'],
    engagement_prediction: 72,
    status: 'pending',
    created_at: '2024-01-20T11:00:00Z'
  },
  {
    id: '3',
    platform: 'facebook',
    content_type: 'educational',
    title: 'Industry Best Practices',
    content: 'What makes a successful digital transformation? Based on our experience with 100+ companies, here are the top 3 factors that determine success...',
    hashtags: ['#DigitalTransformation', '#BestPractices', '#Success'],
    engagement_prediction: 78,
    status: 'approved',
    created_at: '2024-01-20T12:00:00Z'
  }
]

// Components
const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'generator', label: 'Content Generator', icon: Lightbulb },
    { id: 'approval', label: 'Content Approval', icon: CheckCircle },
    { id: 'campaigns', label: 'Campaigns', icon: Target },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'settings', label: 'Settings', icon: Settings }
  ]

  return (
    <div className="w-64 bg-gray-900 text-white h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold">Social Media Agent</h1>
        <p className="text-gray-400 text-sm">SaaS Platform</p>
      </div>
      
      <nav className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === item.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}

const Header = ({ user }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Welcome back, {user?.name}</h2>
          <p className="text-gray-600">{user?.tenant?.name} • {user?.tenant?.plan} plan</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <NotificationDropdown />
          <AccountDropdown user={user} />
        </div>
      </div>
    </header>
  )
}

const Dashboard = () => {
  const stats = [
    { label: 'Active Campaigns', value: '12', change: '+2 this week', icon: Target },
    { label: 'Content Generated', value: '156', change: '+24 this week', icon: Lightbulb },
    { label: 'Approval Rate', value: '87%', change: '+5% this month', icon: CheckCircle },
    { label: 'Engagement Score', value: '8.4', change: '+0.3 this week', icon: TrendingUp }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-sm text-green-600">{stat.change}</p>
                  </div>
                  <Icon className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest content generation and approval activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { action: 'Content approved', platform: 'LinkedIn', time: '2 hours ago' },
                { action: 'Campaign created', platform: 'Multi-platform', time: '4 hours ago' },
                { action: 'Content generated', platform: 'Twitter', time: '6 hours ago' },
                { action: 'Analytics report', platform: 'Facebook', time: '1 day ago' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div>
                    <p className="font-medium">{activity.action}</p>
                    <p className="text-sm text-gray-600">{activity.platform}</p>
                  </div>
                  <span className="text-sm text-gray-500">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Platform Performance</CardTitle>
            <CardDescription>Engagement metrics across platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { platform: 'LinkedIn', engagement: 92, posts: 24 },
                { platform: 'Twitter', engagement: 78, posts: 45 },
                { platform: 'Facebook', engagement: 85, posts: 18 },
                { platform: 'Instagram', engagement: 88, posts: 32 }
              ].map((platform, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold text-sm">
                        {platform.platform.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{platform.platform}</p>
                      <p className="text-sm text-gray-600">{platform.posts} posts</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{platform.engagement}%</p>
                    <p className="text-sm text-gray-600">engagement</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

const GeneratorInterface = () => {
  const [activeStep, setActiveStep] = useState('profile')
  const [businessProfile, setBusinessProfile] = useState({
    company_name: '',
    industry: '',
    target_audience: '',
    brand_voice: 'professional'
  })

  const handleProfileSubmit = (e) => {
    e.preventDefault()
    setActiveStep('strategy')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Content Generator</h3>
          <p className="text-gray-600">Create AI-powered content for your social media platforms</p>
        </div>
        <Button>
          <PlusCircle size={16} className="mr-2" />
          New Campaign
        </Button>
      </div>

      <Tabs value={activeStep} onValueChange={setActiveStep}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">Business Profile</TabsTrigger>
          <TabsTrigger value="strategy">Content Strategy</TabsTrigger>
          <TabsTrigger value="generate">Generate Content</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Business Profile Setup</CardTitle>
              <CardDescription>
                Tell us about your business to generate relevant content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Company Name</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={businessProfile.company_name}
                      onChange={(e) => setBusinessProfile({...businessProfile, company_name: e.target.value})}
                      placeholder="Enter your company name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Industry</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={businessProfile.industry}
                      onChange={(e) => setBusinessProfile({...businessProfile, industry: e.target.value})}
                    >
                      <option value="">Select industry</option>
                      <option value="technology">Technology</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="finance">Finance</option>
                      <option value="education">Education</option>
                      <option value="retail">Retail</option>
                      <option value="manufacturing">Manufacturing</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Target Audience</label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    value={businessProfile.target_audience}
                    onChange={(e) => setBusinessProfile({...businessProfile, target_audience: e.target.value})}
                    placeholder="Describe your target audience..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Brand Voice</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={businessProfile.brand_voice}
                    onChange={(e) => setBusinessProfile({...businessProfile, brand_voice: e.target.value})}
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="casual">Casual</option>
                    <option value="innovative">Innovative</option>
                  </select>
                </div>

                <Button type="submit" className="w-full">
                  Save Profile & Continue
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="strategy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Strategy</CardTitle>
              <CardDescription>
                Configure your content strategy and posting preferences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Platforms</label>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {['Facebook', 'Twitter', 'LinkedIn', 'Instagram', 'TikTok'].map((platform) => (
                      <label key={platform} className="flex items-center space-x-2">
                        <input type="checkbox" className="rounded" defaultChecked />
                        <span className="text-sm">{platform}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Content Types</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {['Educational', 'Promotional', 'Entertaining', 'Inspirational', 'News'].map((type) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input type="checkbox" className="rounded" defaultChecked />
                        <span className="text-sm">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Posting Frequency</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option>Daily</option>
                    <option>3x per week</option>
                    <option>Weekly</option>
                    <option>Custom schedule</option>
                  </select>
                </div>

                <Button onClick={() => setActiveStep('generate')} className="w-full">
                  Create Strategy & Generate Content
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generate" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Generate Content</CardTitle>
              <CardDescription>
                Generate AI-powered content suggestions for your campaigns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Number of Posts</label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                      <option>5 posts</option>
                      <option>10 posts</option>
                      <option>20 posts</option>
                      <option>50 posts</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Campaign Name</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="Enter campaign name"
                    />
                  </div>
                </div>

                <Button className="w-full">
                  <Lightbulb size={16} className="mr-2" />
                  Generate Content Suggestions
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

const ContentApproval = () => {
  const [suggestions, setSuggestions] = useState(mockContentSuggestions)
  const [filter, setFilter] = useState('all')

  const handleApproval = (id, action) => {
    setSuggestions(prev => prev.map(suggestion => 
      suggestion.id === id 
        ? { ...suggestion, status: action }
        : suggestion
    ))
  }

  const filteredSuggestions = suggestions.filter(suggestion => 
    filter === 'all' || suggestion.status === filter
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Content Approval</h3>
          <p className="text-gray-600">Review and approve AI-generated content suggestions</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select 
            className="px-3 py-2 border border-gray-300 rounded-md"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Content</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <Button variant="outline">
            <Filter size={16} className="mr-2" />
            Filters
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredSuggestions.map((suggestion) => (
          <Card key={suggestion.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Badge variant={suggestion.platform === 'linkedin' ? 'default' : 'secondary'}>
                  {suggestion.platform}
                </Badge>
                <Badge variant={
                  suggestion.status === 'approved' ? 'default' :
                  suggestion.status === 'rejected' ? 'destructive' : 'secondary'
                }>
                  {suggestion.status}
                </Badge>
              </div>
              <CardTitle className="text-lg">{suggestion.title}</CardTitle>
              <CardDescription>
                {suggestion.content_type} • {suggestion.engagement_prediction}% predicted engagement
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-3 rounded-md">
                <p className="text-sm">{suggestion.content}</p>
              </div>
              
              <div className="flex flex-wrap gap-1">
                {suggestion.hashtags.map((hashtag, index) => (
                  <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {hashtag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>Engagement: {suggestion.engagement_prediction}%</span>
                <span>{new Date(suggestion.created_at).toLocaleDateString()}</span>
              </div>

              {suggestion.status === 'pending' && (
                <div className="flex items-center space-x-2 pt-2">
                  <Button 
                    size="sm" 
                    onClick={() => handleApproval(suggestion.id, 'approved')}
                    className="flex-1"
                  >
                    <CheckCircle size={14} className="mr-1" />
                    Approve
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleApproval(suggestion.id, 'thumbs_up')}
                  >
                    <ThumbsUp size={14} />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleApproval(suggestion.id, 'thumbs_down')}
                  >
                    <ThumbsDown size={14} />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="destructive"
                    onClick={() => handleApproval(suggestion.id, 'rejected')}
                  >
                    <XCircle size={14} />
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

const MainContent = ({ activeTab, user }) => {
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'generator':
        return <EnhancedGeneratorInterface />
      case 'approval':
        return <EnhancedContentApproval />
      case 'campaigns':
        return <CampaignsPage />
        
      case 'analytics':
        return <AnalyticsPage />
        
      case 'settings':
        return <SettingsPage />
        
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Header user={user} />
      <main className="flex-1 p-6 bg-gray-50">
        {renderContent()}
      </main>
    </div>
  )
}

function App() {
  const { user, loading } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Social Media Agent...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Welcome to Social Media Agent</CardTitle>
            <CardDescription>Sign in to access your SaaS platform</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full">Sign In</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <MainContent activeTab={activeTab} user={user} />
    </div>
  )
}

export default App

