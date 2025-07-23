import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  PlusCircle, 
  Play, 
  Pause, 
  Edit, 
  Trash2, 
  BarChart3,
  Calendar,
  Target,
  Users,
  TrendingUp,
  Eye,
  EyeOff
} from 'lucide-react'

const CampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([
    {
      id: 1,
      name: 'Summer Sale 2025',
      status: 'active',
      platforms: ['facebook', 'instagram', 'twitter'],
      posts_generated: 24,
      posts_published: 18,
      engagement_rate: 4.2,
      reach: 15420,
      start_date: '2025-07-01',
      end_date: '2025-07-31',
      description: 'Promote our summer collection with engaging content across social media platforms. Focus on lifestyle imagery and customer testimonials.'
    },
    {
      id: 2,
      name: 'Product Launch - AI Tools',
      status: 'paused',
      platforms: ['linkedin', 'twitter'],
      posts_generated: 12,
      posts_published: 8,
      engagement_rate: 6.8,
      reach: 8930,
      start_date: '2025-07-15',
      end_date: '2025-08-15',
      description: 'Launch campaign for our new AI-powered productivity tools targeting business professionals and entrepreneurs.'
    },
    {
      id: 3,
      name: 'Brand Awareness Q3',
      status: 'draft',
      platforms: ['facebook', 'instagram', 'linkedin', 'tiktok'],
      posts_generated: 0,
      posts_published: 0,
      engagement_rate: 0,
      reach: 0,
      start_date: '2025-08-01',
      end_date: '2025-09-30',
      description: 'Comprehensive brand awareness campaign to increase visibility and establish thought leadership in our industry.'
    }
  ])

  const [expandedCards, setExpandedCards] = useState(new Set())

  const toggleCardExpansion = (id) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'paused': return 'bg-yellow-100 text-yellow-800'
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleStatusChange = (id, newStatus) => {
    setCampaigns(prev => prev.map(campaign => 
      campaign.id === id ? { ...campaign, status: newStatus } : campaign
    ))
  }

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Campaigns</h3>
          <p className="text-gray-600">Manage your social media campaigns and track performance</p>
        </div>
        <Button>
          <PlusCircle size={16} className="mr-2" />
          Create Campaign
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{campaigns.length}</div>
                <div className="text-sm text-gray-600">Total Campaigns</div>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{campaigns.filter(c => c.status === 'active').length}</div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              <Play className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{campaigns.reduce((sum, c) => sum + c.posts_published, 0)}</div>
                <div className="text-sm text-gray-600">Posts Published</div>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{(campaigns.reduce((sum, c) => sum + c.reach, 0) / 1000).toFixed(1)}K</div>
                <div className="text-sm text-gray-600">Total Reach</div>
              </div>
              <Users className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {campaigns.map((campaign) => {
          const isExpanded = expandedCards.has(campaign.id)
          const shouldTruncate = campaign.description.length > 100

          return (
            <Card key={campaign.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{campaign.name}</CardTitle>
                  <Badge className={getStatusColor(campaign.status)}>
                    {campaign.status}
                  </Badge>
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {campaign.platforms.map(platform => (
                    <Badge key={platform} variant="outline" className="text-xs">
                      {platform}
                    </Badge>
                  ))}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {shouldTruncate && !isExpanded 
                      ? truncateText(campaign.description)
                      : campaign.description
                    }
                  </p>
                  
                  {shouldTruncate && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleCardExpansion(campaign.id)}
                      className="mt-2 p-0 h-auto text-blue-600 hover:text-blue-800"
                    >
                      {isExpanded ? (
                        <>
                          <EyeOff className="h-3 w-3 mr-1" />
                          View Less
                        </>
                      ) : (
                        <>
                          <Eye className="h-3 w-3 mr-1" />
                          View More
                        </>
                      )}
                    </Button>
                  )}
                </div>

                {/* Campaign Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600">Posts Generated</div>
                    <div className="font-semibold">{campaign.posts_generated}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Published</div>
                    <div className="font-semibold">{campaign.posts_published}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Engagement Rate</div>
                    <div className="font-semibold">{campaign.engagement_rate}%</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Reach</div>
                    <div className="font-semibold">{campaign.reach.toLocaleString()}</div>
                  </div>
                </div>

                {/* Campaign Duration */}
                <div className="flex items-center text-xs text-gray-500">
                  <Calendar className="h-3 w-3 mr-1" />
                  {campaign.start_date} - {campaign.end_date}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 pt-2 border-t">
                  {campaign.status === 'active' ? (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleStatusChange(campaign.id, 'paused')}
                      className="flex-1"
                    >
                      <Pause size={14} className="mr-1" />
                      Pause
                    </Button>
                  ) : campaign.status === 'paused' ? (
                    <Button 
                      size="sm" 
                      onClick={() => handleStatusChange(campaign.id, 'active')}
                      className="flex-1"
                    >
                      <Play size={14} className="mr-1" />
                      Resume
                    </Button>
                  ) : (
                    <Button 
                      size="sm" 
                      onClick={() => handleStatusChange(campaign.id, 'active')}
                      className="flex-1"
                    >
                      <Play size={14} className="mr-1" />
                      Start
                    </Button>
                  )}
                  
                  <Button size="sm" variant="outline">
                    <Edit size={14} className="mr-1" />
                    Edit
                  </Button>
                  
                  <Button size="sm" variant="outline">
                    <BarChart3 size={14} className="mr-1" />
                    Analytics
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export default CampaignsPage
