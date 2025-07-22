import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'
import { 
  TrendingUp, TrendingDown, ThumbsUp, ThumbsDown, 
  CheckCircle, XCircle, Target, Users, Calendar,
  Download, Filter, RefreshCw, AlertCircle, Lightbulb
} from 'lucide-react'

// Mock data for analytics
const mockFeedbackData = [
  { date: '2024-01-15', approvals: 12, rejections: 3, thumbsUp: 8, thumbsDown: 2 },
  { date: '2024-01-16', approvals: 15, rejections: 2, thumbsUp: 10, thumbsDown: 1 },
  { date: '2024-01-17', approvals: 18, rejections: 4, thumbsUp: 12, thumbsDown: 3 },
  { date: '2024-01-18', approvals: 14, rejections: 1, thumbsUp: 9, thumbsDown: 0 },
  { date: '2024-01-19', approvals: 20, rejections: 3, thumbsUp: 15, thumbsDown: 2 },
  { date: '2024-01-20', approvals: 16, rejections: 2, thumbsUp: 11, thumbsDown: 1 }
]

const mockPlatformPerformance = [
  { platform: 'LinkedIn', approvalRate: 92, avgEngagement: 8.4, totalContent: 24 },
  { platform: 'Twitter', approvalRate: 78, avgEngagement: 6.2, totalContent: 45 },
  { platform: 'Facebook', approvalRate: 85, avgEngagement: 7.1, totalContent: 18 },
  { platform: 'Instagram', approvalRate: 88, avgEngagement: 7.8, totalContent: 32 },
  { platform: 'TikTok', approvalRate: 75, avgEngagement: 9.2, totalContent: 12 }
]

const mockContentTypePerformance = [
  { type: 'Educational', value: 35, approvalRate: 89 },
  { type: 'Promotional', value: 25, approvalRate: 72 },
  { type: 'Entertaining', value: 20, approvalRate: 85 },
  { type: 'Inspirational', value: 15, approvalRate: 91 },
  { type: 'News', value: 5, approvalRate: 68 }
]

const mockRecommendations = [
  {
    id: '1',
    type: 'Content Strategy',
    title: 'Increase Educational Content',
    description: 'Based on your approval patterns, educational content performs 23% better than promotional content.',
    confidence: 87,
    impact: 'High',
    basedOn: '156 similar businesses',
    action: 'Adjust content mix to 45% educational, 30% promotional'
  },
  {
    id: '2',
    type: 'Platform Focus',
    title: 'Optimize LinkedIn Posting',
    description: 'Your LinkedIn content has 92% approval rate. Consider increasing posting frequency.',
    confidence: 94,
    impact: 'Medium',
    basedOn: '89 feedback points',
    action: 'Increase LinkedIn posts from 3 to 5 per week'
  },
  {
    id: '3',
    type: 'Timing',
    title: 'Post During Peak Hours',
    description: 'Content posted between 9-11 AM receives 34% more positive feedback.',
    confidence: 76,
    impact: 'Medium',
    basedOn: '234 timing data points',
    action: 'Schedule more posts during 9-11 AM window'
  }
]

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

const AnalyticsDashboard = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')
  const [isLoading, setIsLoading] = useState(false)

  const handleRefresh = () => {
    setIsLoading(true)
    // Simulate API call
    setTimeout(() => setIsLoading(false), 2000)
  }

  const FeedbackOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Approvals</p>
              <p className="text-2xl font-bold text-green-600">95</p>
              <p className="text-sm text-green-600">+12% from last week</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Rejections</p>
              <p className="text-2xl font-bold text-red-600">15</p>
              <p className="text-sm text-red-600">-8% from last week</p>
            </div>
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Thumbs Up</p>
              <p className="text-2xl font-bold text-blue-600">65</p>
              <p className="text-sm text-blue-600">+18% from last week</p>
            </div>
            <ThumbsUp className="h-8 w-8 text-blue-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Approval Rate</p>
              <p className="text-2xl font-bold text-purple-600">86.4%</p>
              <p className="text-sm text-purple-600">+5.2% from last week</p>
            </div>
            <Target className="h-8 w-8 text-purple-600" />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const FeedbackTrends = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Feedback Trends</CardTitle>
        <CardDescription>Daily feedback patterns over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={mockFeedbackData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="approvals" stroke="#10B981" strokeWidth={2} name="Approvals" />
            <Line type="monotone" dataKey="rejections" stroke="#EF4444" strokeWidth={2} name="Rejections" />
            <Line type="monotone" dataKey="thumbsUp" stroke="#3B82F6" strokeWidth={2} name="Thumbs Up" />
            <Line type="monotone" dataKey="thumbsDown" stroke="#F59E0B" strokeWidth={2} name="Thumbs Down" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )

  const PlatformAnalysis = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <Card>
        <CardHeader>
          <CardTitle>Platform Performance</CardTitle>
          <CardDescription>Approval rates and engagement by platform</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockPlatformPerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="platform" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="approvalRate" fill="#10B981" name="Approval Rate %" />
              <Bar dataKey="avgEngagement" fill="#3B82F6" name="Avg Engagement" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Content Type Distribution</CardTitle>
          <CardDescription>Performance by content type</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={mockContentTypePerformance}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ type, value }) => `${type}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {mockContentTypePerformance.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )

  const RecommendationsPanel = () => (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              AI Recommendations
            </CardTitle>
            <CardDescription>
              Personalized suggestions based on your content performance and similar businesses
            </CardDescription>
          </div>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockRecommendations.map((rec) => (
            <div key={rec.id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline">{rec.type}</Badge>
                    <Badge variant={rec.impact === 'High' ? 'default' : 'secondary'}>
                      {rec.impact} Impact
                    </Badge>
                  </div>
                  <h4 className="font-semibold text-lg">{rec.title}</h4>
                  <p className="text-gray-600 mb-2">{rec.description}</p>
                  <p className="text-sm font-medium text-blue-600">{rec.action}</p>
                </div>
                <div className="text-right ml-4">
                  <div className="text-2xl font-bold text-green-600">{rec.confidence}%</div>
                  <div className="text-sm text-gray-500">confidence</div>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>Based on {rec.basedOn}</span>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline">
                    Implement
                  </Button>
                  <Button size="sm" variant="ghost">
                    Dismiss
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const DetailedMetrics = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Platform Breakdown</CardTitle>
          <CardDescription>Detailed performance metrics by platform</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockPlatformPerformance.map((platform, index) => (
              <div key={platform.platform} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold text-sm">
                      {platform.platform.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{platform.platform}</p>
                    <p className="text-sm text-gray-600">{platform.totalContent} posts</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{platform.approvalRate}%</p>
                  <p className="text-sm text-gray-600">approval rate</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Feedback</CardTitle>
          <CardDescription>Latest user feedback on generated content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { platform: 'LinkedIn', action: 'Approved', content: 'The Future of AI in Business', time: '2 hours ago' },
              { platform: 'Twitter', action: 'Thumbs Up', content: 'New Product Launch', time: '4 hours ago' },
              { platform: 'Facebook', action: 'Approved', content: 'Industry Best Practices', time: '6 hours ago' },
              { platform: 'Instagram', action: 'Thumbs Down', content: 'Behind the Scenes', time: '8 hours ago' },
              { platform: 'LinkedIn', action: 'Rejected', content: 'Market Analysis', time: '1 day ago' }
            ].map((feedback, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center space-x-3">
                  <Badge variant={
                    feedback.action === 'Approved' ? 'default' :
                    feedback.action === 'Thumbs Up' ? 'secondary' :
                    feedback.action === 'Thumbs Down' ? 'outline' : 'destructive'
                  }>
                    {feedback.action}
                  </Badge>
                  <div>
                    <p className="font-medium text-sm">{feedback.content}</p>
                    <p className="text-xs text-gray-600">{feedback.platform}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{feedback.time}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Analytics Dashboard</h3>
          <p className="text-gray-600">Content performance insights and AI-powered recommendations</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select 
            className="px-3 py-2 border border-gray-300 rounded-md"
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <FeedbackOverview />
          <FeedbackTrends />
          <PlatformAnalysis />
        </TabsContent>

        <TabsContent value="platforms" className="space-y-6">
          <PlatformAnalysis />
          <DetailedMetrics />
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <RecommendationsPanel />
          <Card>
            <CardHeader>
              <CardTitle>Implementation History</CardTitle>
              <CardDescription>Track the success of implemented recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { recommendation: 'Increase educational content', implemented: '2024-01-15', result: '+23% approval rate', status: 'success' },
                  { recommendation: 'Post during peak hours', implemented: '2024-01-10', result: '+15% engagement', status: 'success' },
                  { recommendation: 'Focus on LinkedIn', implemented: '2024-01-05', result: '+8% reach', status: 'partial' }
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{item.recommendation}</p>
                      <p className="text-sm text-gray-600">Implemented on {item.implemented}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600">{item.result}</p>
                      <Badge variant={item.status === 'success' ? 'default' : 'secondary'}>
                        {item.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Business Insights</CardTitle>
                <CardDescription>Insights from similar businesses in your industry</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900">Industry Benchmark</h4>
                    <p className="text-blue-700">Your approval rate (86.4%) is 12% above the technology industry average (74.2%)</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-900">Top Performing Content</h4>
                    <p className="text-green-700">Educational content performs best in your industry with 89% average approval rate</p>
                  </div>
                  <div className="p-4 bg-yellow-50 rounded-lg">
                    <h4 className="font-semibold text-yellow-900">Growth Opportunity</h4>
                    <p className="text-yellow-700">Similar businesses see 34% better engagement with video content</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Predictive Analytics</CardTitle>
                <CardDescription>AI predictions for your content performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Next Week Prediction</p>
                      <p className="text-sm text-gray-600">Based on current trends</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-green-600">91%</p>
                      <p className="text-sm text-gray-600">approval rate</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Optimal Posting Time</p>
                      <p className="text-sm text-gray-600">For maximum engagement</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">9:30 AM</p>
                      <p className="text-sm text-gray-600">weekdays</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Content Mix Suggestion</p>
                      <p className="text-sm text-gray-600">For optimal performance</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">45% Educational</p>
                      <p className="text-sm text-gray-600">30% Promotional, 25% Other</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AnalyticsDashboard

