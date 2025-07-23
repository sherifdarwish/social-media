import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Heart,
  MessageSquare,
  Share2,
  Eye,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Download,
  Filter,
  Calendar,
  RefreshCw
} from 'lucide-react'

const Analytics = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  const [selectedPlatforms, setSelectedPlatforms] = useState(['all'])

  const overallStats = {
    totalPosts: 156,
    totalReach: 45200,
    totalEngagement: 3840,
    avgEngagementRate: 8.5,
    totalFollowers: 12400,
    growthRate: 12.3
  }

  const platformStats = [
    {
      platform: 'facebook',
      icon: '📘',
      posts: 42,
      reach: 15600,
      engagement: 1240,
      engagementRate: 7.9,
      followers: 3200,
      growth: 8.5
    },
    {
      platform: 'twitter',
      icon: '🐦',
      posts: 58,
      reach: 12800,
      engagement: 1580,
      engagementRate: 12.3,
      followers: 4800,
      growth: 15.2
    },
    {
      platform: 'instagram',
      icon: '📷',
      posts: 28,
      reach: 9400,
      engagement: 820,
      engagementRate: 8.7,
      followers: 2900,
      growth: 10.1
    },
    {
      platform: 'linkedin',
      icon: '💼',
      posts: 24,
      reach: 5800,
      engagement: 180,
      engagementRate: 3.1,
      followers: 1350,
      growth: 5.8
    },
    {
      platform: 'tiktok',
      icon: '🎵',
      posts: 4,
      reach: 1600,
      engagement: 20,
      engagementRate: 1.25,
      followers: 150,
      growth: 25.0
    }
  ]

  const recentErrors = [
    {
      id: 1,
      timestamp: '2025-07-22 14:30',
      platform: 'facebook',
      type: 'API_RATE_LIMIT',
      message: 'Rate limit exceeded for Facebook Graph API',
      status: 'resolved',
      impact: 'medium'
    },
    {
      id: 2,
      timestamp: '2025-07-22 12:15',
      platform: 'twitter',
      type: 'AUTH_ERROR',
      message: 'Twitter OAuth token expired',
      status: 'active',
      impact: 'high'
    },
    {
      id: 3,
      timestamp: '2025-07-22 09:45',
      platform: 'instagram',
      type: 'CONTENT_REJECTED',
      message: 'Post rejected due to content policy violation',
      status: 'resolved',
      impact: 'low'
    },
    {
      id: 4,
      timestamp: '2025-07-21 16:20',
      platform: 'linkedin',
      type: 'NETWORK_ERROR',
      message: 'Connection timeout while posting to LinkedIn',
      status: 'resolved',
      impact: 'medium'
    }
  ]

  const topPerformingPosts = [
    {
      id: 1,
      platform: 'twitter',
      content: 'Just launched our new AI-powered social media tool! 🚀 #AI #SocialMedia',
      engagement: 245,
      reach: 3200,
      likes: 189,
      shares: 34,
      comments: 22,
      timestamp: '2025-07-21 15:30'
    },
    {
      id: 2,
      platform: 'instagram',
      content: 'Behind the scenes of our product development process 📸',
      engagement: 198,
      reach: 2800,
      likes: 156,
      shares: 28,
      comments: 14,
      timestamp: '2025-07-20 18:45'
    },
    {
      id: 3,
      platform: 'facebook',
      content: 'Customer success story: How Company X increased their social media ROI by 300%',
      engagement: 167,
      reach: 2400,
      likes: 134,
      shares: 21,
      comments: 12,
      timestamp: '2025-07-19 10:15'
    }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'bg-green-100 text-green-800'
      case 'active': return 'bg-red-100 text-red-800'
      case 'investigating': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'text-red-600'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-gray-600">Track performance and monitor system health</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download size={16} className="mr-2" />
            Export Report
          </Button>
          <Button variant="outline">
            <RefreshCw size={16} className="mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <select 
          className="px-3 py-2 border border-gray-300 rounded-md"
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
        >
          <option value="24h">Last 24 hours</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
        <Button variant="outline">
          <Filter size={16} className="mr-2" />
          Filter Platforms
        </Button>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="platforms">Platform Details</TabsTrigger>
          <TabsTrigger value="content">Content Performance</TabsTrigger>
          <TabsTrigger value="errors">Error Tracking</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Overall Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Posts</p>
                    <p className="text-2xl font-bold">{overallStats.totalPosts}</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Reach</p>
                    <p className="text-2xl font-bold">{overallStats.totalReach.toLocaleString()}</p>
                  </div>
                  <Eye className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Engagement</p>
                    <p className="text-2xl font-bold">{overallStats.totalEngagement.toLocaleString()}</p>
                  </div>
                  <Heart className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Avg. Engagement</p>
                    <p className="text-2xl font-bold">{overallStats.avgEngagementRate}%</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Followers</p>
                    <p className="text-2xl font-bold">{overallStats.totalFollowers.toLocaleString()}</p>
                  </div>
                  <Users className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Growth Rate</p>
                    <p className="text-2xl font-bold text-green-600">+{overallStats.growthRate}%</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Platform Performance Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Platform Performance Summary</CardTitle>
              <CardDescription>Quick overview of all platform metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {platformStats.map((platform) => (
                  <div key={platform.platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{platform.icon}</span>
                      <div>
                        <h3 className="font-medium capitalize">{platform.platform}</h3>
                        <p className="text-sm text-gray-600">{platform.posts} posts</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-4 gap-8 text-center">
                      <div>
                        <p className="text-lg font-bold">{platform.reach.toLocaleString()}</p>
                        <p className="text-xs text-gray-600">Reach</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold">{platform.engagement}</p>
                        <p className="text-xs text-gray-600">Engagement</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold">{platform.engagementRate}%</p>
                        <p className="text-xs text-gray-600">Rate</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-green-600">+{platform.growth}%</p>
                        <p className="text-xs text-gray-600">Growth</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="platforms" className="space-y-6">
          <div className="grid gap-6">
            {platformStats.map((platform) => (
              <Card key={platform.platform}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">{platform.icon}</span>
                    {platform.platform.charAt(0).toUpperCase() + platform.platform.slice(1)} Analytics
                  </CardTitle>
                  <CardDescription>Detailed performance metrics for {platform.platform}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{platform.posts}</div>
                      <div className="text-sm text-gray-600">Posts Published</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{platform.reach.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Total Reach</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{platform.engagement}</div>
                      <div className="text-sm text-gray-600">Total Engagement</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{platform.followers.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Followers</div>
                    </div>
                  </div>
                  
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <p className="text-gray-500">Chart visualization would go here</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="content" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Posts</CardTitle>
              <CardDescription>Your best content from the selected period</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topPerformingPosts.map((post) => (
                  <div key={post.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">
                          {platformStats.find(p => p.platform === post.platform)?.icon}
                        </span>
                        <Badge variant="outline" className="capitalize">
                          {post.platform}
                        </Badge>
                        <span className="text-sm text-gray-500">{post.timestamp}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-600">{post.engagement}</div>
                        <div className="text-xs text-gray-600">Total Engagement</div>
                      </div>
                    </div>
                    
                    <p className="text-gray-800 mb-3">{post.content}</p>
                    
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="flex items-center justify-center gap-1">
                          <Eye size={14} />
                          <span className="font-medium">{post.reach}</span>
                        </div>
                        <div className="text-xs text-gray-600">Reach</div>
                      </div>
                      <div>
                        <div className="flex items-center justify-center gap-1">
                          <Heart size={14} />
                          <span className="font-medium">{post.likes}</span>
                        </div>
                        <div className="text-xs text-gray-600">Likes</div>
                      </div>
                      <div>
                        <div className="flex items-center justify-center gap-1">
                          <Share2 size={14} />
                          <span className="font-medium">{post.shares}</span>
                        </div>
                        <div className="text-xs text-gray-600">Shares</div>
                      </div>
                      <div>
                        <div className="flex items-center justify-center gap-1">
                          <MessageSquare size={14} />
                          <span className="font-medium">{post.comments}</span>
                        </div>
                        <div className="text-xs text-gray-600">Comments</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Issues</p>
                    <p className="text-2xl font-bold text-red-600">
                      {recentErrors.filter(e => e.status === 'active').length}
                    </p>
                  </div>
                  <XCircle className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Resolved Today</p>
                    <p className="text-2xl font-bold text-green-600">
                      {recentErrors.filter(e => e.status === 'resolved').length}
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">System Uptime</p>
                    <p className="text-2xl font-bold text-green-600">99.8%</p>
                  </div>
                  <Clock className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Errors & Issues</CardTitle>
              <CardDescription>System errors and their resolution status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentErrors.map((error) => (
                  <div key={error.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className={`h-5 w-5 ${getImpactColor(error.impact)}`} />
                        <span className="font-medium">{error.type.replace('_', ' ')}</span>
                        <Badge className={getStatusColor(error.status)}>
                          {error.status}
                        </Badge>
                        <Badge variant="outline" className="capitalize">
                          {error.platform}
                        </Badge>
                      </div>
                      <span className="text-sm text-gray-500">{error.timestamp}</span>
                    </div>
                    <p className="text-gray-700 mb-2">{error.message}</p>
                    <div className="flex justify-between items-center">
                      <span className={`text-sm font-medium ${getImpactColor(error.impact)}`}>
                        {error.impact.toUpperCase()} IMPACT
                      </span>
                      {error.status === 'active' && (
                        <Button size="sm" variant="outline">
                          Investigate
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Analytics
