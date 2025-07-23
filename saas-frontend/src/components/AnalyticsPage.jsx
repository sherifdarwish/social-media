import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
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
  RefreshCw,
  Download,
  Calendar
} from 'lucide-react'

const AnalyticsPage = () => {
  const [timeRange, setTimeRange] = useState('7d')
  const [selectedPlatform, setSelectedPlatform] = useState('all')

  const platformMetrics = [
    {
      platform: 'Facebook',
      posts: 24,
      reach: 15420,
      engagement: 1240,
      engagement_rate: 8.04,
      clicks: 320,
      shares: 45,
      comments: 89,
      likes: 1106,
      trend: 'up',
      trend_value: 12.5
    },
    {
      platform: 'Instagram',
      posts: 18,
      reach: 12300,
      engagement: 980,
      engagement_rate: 7.97,
      clicks: 245,
      shares: 32,
      comments: 67,
      likes: 881,
      trend: 'up',
      trend_value: 8.3
    },
    {
      platform: 'Twitter',
      posts: 32,
      reach: 8900,
      engagement: 445,
      engagement_rate: 5.00,
      clicks: 156,
      shares: 78,
      comments: 34,
      likes: 333,
      trend: 'down',
      trend_value: -3.2
    },
    {
      platform: 'LinkedIn',
      posts: 12,
      reach: 5600,
      engagement: 420,
      engagement_rate: 7.50,
      clicks: 89,
      shares: 23,
      comments: 45,
      likes: 352,
      trend: 'up',
      trend_value: 15.7
    },
    {
      platform: 'TikTok',
      posts: 8,
      reach: 22100,
      engagement: 1890,
      engagement_rate: 8.55,
      clicks: 445,
      shares: 234,
      comments: 123,
      likes: 1533,
      trend: 'up',
      trend_value: 28.4
    }
  ]

  const errorLogs = [
    {
      id: 1,
      timestamp: '2025-07-22 14:30:25',
      platform: 'Twitter',
      error_type: 'API Rate Limit',
      message: 'Rate limit exceeded for posting endpoint',
      status: 'resolved',
      impact: 'medium',
      affected_posts: 3
    },
    {
      id: 2,
      timestamp: '2025-07-22 12:15:10',
      platform: 'Instagram',
      error_type: 'Authentication Failed',
      message: 'Access token expired, requires re-authentication',
      status: 'active',
      impact: 'high',
      affected_posts: 8
    },
    {
      id: 3,
      timestamp: '2025-07-22 09:45:33',
      platform: 'Facebook',
      error_type: 'Content Violation',
      message: 'Post rejected due to community guidelines',
      status: 'resolved',
      impact: 'low',
      affected_posts: 1
    },
    {
      id: 4,
      timestamp: '2025-07-22 08:20:15',
      platform: 'LinkedIn',
      error_type: 'Network Timeout',
      message: 'Connection timeout while posting content',
      status: 'resolved',
      impact: 'medium',
      affected_posts: 2
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'resolved': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'active': return <XCircle className="h-4 w-4 text-red-600" />
      case 'investigating': return <Clock className="h-4 w-4 text-yellow-600" />
      default: return <AlertTriangle className="h-4 w-4 text-gray-600" />
    }
  }

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const totalMetrics = platformMetrics.reduce((acc, platform) => ({
    posts: acc.posts + platform.posts,
    reach: acc.reach + platform.reach,
    engagement: acc.engagement + platform.engagement,
    clicks: acc.clicks + platform.clicks,
    shares: acc.shares + platform.shares,
    comments: acc.comments + platform.comments,
    likes: acc.likes + platform.likes
  }), { posts: 0, reach: 0, engagement: 0, clicks: 0, shares: 0, comments: 0, likes: 0 })

  const avgEngagementRate = (totalMetrics.engagement / totalMetrics.reach * 100).toFixed(2)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Analytics & Performance</h3>
          <p className="text-gray-600">Track your social media performance and monitor system health</p>
        </div>
        <div className="flex items-center space-x-3">
          <select 
            className="px-3 py-2 border border-gray-300 rounded-md"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{totalMetrics.posts}</div>
                <div className="text-sm text-gray-600">Posts</div>
              </div>
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{(totalMetrics.reach / 1000).toFixed(1)}K</div>
                <div className="text-sm text-gray-600">Reach</div>
              </div>
              <Users className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{totalMetrics.engagement}</div>
                <div className="text-sm text-gray-600">Engagement</div>
              </div>
              <Heart className="h-6 w-6 text-red-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{avgEngagementRate}%</div>
                <div className="text-sm text-gray-600">Avg Rate</div>
              </div>
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{totalMetrics.clicks}</div>
                <div className="text-sm text-gray-600">Clicks</div>
              </div>
              <Eye className="h-6 w-6 text-indigo-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{totalMetrics.shares}</div>
                <div className="text-sm text-gray-600">Shares</div>
              </div>
              <Share2 className="h-6 w-6 text-orange-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{totalMetrics.comments}</div>
                <div className="text-sm text-gray-600">Comments</div>
              </div>
              <MessageSquare className="h-6 w-6 text-teal-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Platform Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Performance</CardTitle>
          <CardDescription>Detailed metrics for each social media platform</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Platform</th>
                  <th className="text-right py-2">Posts</th>
                  <th className="text-right py-2">Reach</th>
                  <th className="text-right py-2">Engagement</th>
                  <th className="text-right py-2">Rate</th>
                  <th className="text-right py-2">Clicks</th>
                  <th className="text-right py-2">Trend</th>
                </tr>
              </thead>
              <tbody>
                {platformMetrics.map((platform) => (
                  <tr key={platform.platform} className="border-b hover:bg-gray-50">
                    <td className="py-3">
                      <div className="font-medium">{platform.platform}</div>
                    </td>
                    <td className="text-right py-3">{platform.posts}</td>
                    <td className="text-right py-3">{platform.reach.toLocaleString()}</td>
                    <td className="text-right py-3">{platform.engagement}</td>
                    <td className="text-right py-3">{platform.engagement_rate}%</td>
                    <td className="text-right py-3">{platform.clicks}</td>
                    <td className="text-right py-3">
                      <div className={`flex items-center justify-end ${
                        platform.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {platform.trend === 'up' ? (
                          <TrendingUp className="h-4 w-4 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 mr-1" />
                        )}
                        {Math.abs(platform.trend_value)}%
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Error Tracking */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Error Tracking & System Health</CardTitle>
              <CardDescription>Monitor system errors and platform issues</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-green-600">
                <CheckCircle className="h-3 w-3 mr-1" />
                System Healthy
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {errorLogs.map((error) => (
              <div key={error.id} className="flex items-start space-x-4 p-4 border rounded-lg hover:bg-gray-50">
                <div className="mt-0.5">
                  {getStatusIcon(error.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{error.platform}</span>
                      <Badge variant="outline">{error.error_type}</Badge>
                      <Badge className={getImpactColor(error.impact)}>
                        {error.impact} impact
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-500">
                      {error.timestamp}
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{error.message}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-gray-500">
                      Affected posts: {error.affected_posts}
                    </span>
                    <Badge variant={error.status === 'resolved' ? 'default' : 'destructive'}>
                      {error.status}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">API Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {['Facebook', 'Instagram', 'Twitter', 'LinkedIn', 'TikTok'].map(platform => (
                <div key={platform} className="flex items-center justify-between">
                  <span className="text-sm">{platform}</span>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Online
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">AI Services</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Content Generation</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Active
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Image Processing</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Active
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Analytics Engine</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Active
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Response Time</span>
                <span className="text-sm font-medium text-green-600">245ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Uptime</span>
                <span className="text-sm font-medium text-green-600">99.9%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Success Rate</span>
                <span className="text-sm font-medium text-green-600">98.7%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AnalyticsPage
