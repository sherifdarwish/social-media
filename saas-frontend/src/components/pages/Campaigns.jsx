import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  PlusCircle, 
  Target, 
  Calendar,
  TrendingUp,
  Play,
  Pause,
  Edit,
  Trash2,
  Eye,
  MoreHorizontal
} from 'lucide-react'

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([
    {
      id: 1,
      name: "Summer Product Launch",
      status: "active",
      platforms: ["facebook", "twitter", "instagram", "linkedin"],
      postsGenerated: 24,
      postsScheduled: 18,
      engagement: 8.5,
      reach: 12400,
      startDate: "2025-07-01",
      endDate: "2025-08-31"
    },
    {
      id: 2,
      name: "Brand Awareness Q3",
      status: "paused",
      platforms: ["twitter", "linkedin"],
      postsGenerated: 15,
      postsScheduled: 10,
      engagement: 6.2,
      reach: 8900,
      startDate: "2025-07-15",
      endDate: "2025-09-30"
    },
    {
      id: 3,
      name: "Holiday Campaign 2025",
      status: "draft",
      platforms: ["facebook", "instagram", "tiktok"],
      postsGenerated: 0,
      postsScheduled: 0,
      engagement: 0,
      reach: 0,
      startDate: "2025-12-01",
      endDate: "2025-12-31"
    }
  ])

  const [showCreateModal, setShowCreateModal] = useState(false)

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'paused': return 'bg-yellow-100 text-yellow-800'
      case 'draft': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
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
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <p className="text-gray-600">Manage your social media campaigns</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <PlusCircle size={16} className="mr-2" />
          Create Campaign
        </Button>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All Campaigns</TabsTrigger>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="paused">Paused</TabsTrigger>
          <TabsTrigger value="draft">Drafts</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <div className="grid gap-4">
            {campaigns.map((campaign) => (
              <Card key={campaign.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Target size={20} />
                        {campaign.name}
                        <Badge className={getStatusColor(campaign.status)}>
                          {campaign.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        {campaign.startDate} - {campaign.endDate}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye size={16} />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit size={16} />
                      </Button>
                      <Button variant="outline" size="sm">
                        <MoreHorizontal size={16} />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{campaign.postsGenerated}</div>
                      <div className="text-sm text-gray-600">Posts Generated</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{campaign.postsScheduled}</div>
                      <div className="text-sm text-gray-600">Posts Scheduled</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{campaign.engagement}%</div>
                      <div className="text-sm text-gray-600">Engagement</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{campaign.reach.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Reach</div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex gap-1">
                      {campaign.platforms.map((platform) => (
                        <span key={platform} className="text-lg" title={platform}>
                          {getPlatformIcon(platform)}
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      {campaign.status === 'active' ? (
                        <Button variant="outline" size="sm">
                          <Pause size={16} className="mr-1" />
                          Pause
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm">
                          <Play size={16} className="mr-1" />
                          Start
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <TrendingUp size={16} className="mr-1" />
                        Analytics
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="active">
          <div className="grid gap-4">
            {campaigns.filter(c => c.status === 'active').map((campaign) => (
              <Card key={campaign.id}>
                <CardHeader>
                  <CardTitle>{campaign.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Active campaign details...</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="paused">
          <div className="grid gap-4">
            {campaigns.filter(c => c.status === 'paused').map((campaign) => (
              <Card key={campaign.id}>
                <CardHeader>
                  <CardTitle>{campaign.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Paused campaign details...</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="draft">
          <div className="grid gap-4">
            {campaigns.filter(c => c.status === 'draft').map((campaign) => (
              <Card key={campaign.id}>
                <CardHeader>
                  <CardTitle>{campaign.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Draft campaign details...</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Campaign Modal would go here */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Create New Campaign</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Campaign Name</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter campaign name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Platforms</label>
                <div className="space-y-2">
                  {['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok'].map((platform) => (
                    <label key={platform} className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="mr-2">{getPlatformIcon(platform)}</span>
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={() => setShowCreateModal(false)} variant="outline">
                  Cancel
                </Button>
                <Button onClick={() => setShowCreateModal(false)}>
                  Create Campaign
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Campaigns
