import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  CheckCircle, 
  XCircle, 
  ThumbsUp, 
  ThumbsDown,
  Filter,
  Search,
  MoreHorizontal,
  Eye,
  EyeOff,
  Calendar,
  Clock,
  AlertCircle,
  Loader2
} from 'lucide-react'

const EnhancedContentApproval = () => {
  const [suggestions, setSuggestions] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedCards, setExpandedCards] = useState(new Set())

  // Load content suggestions on component mount
  useEffect(() => {
    loadContentSuggestions()
  }, [])

  const loadContentSuggestions = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/content/suggestions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to load content suggestions')
      }

      const data = await response.json()
      setSuggestions(data.suggestions || [])
    } catch (err) {
      setError(err.message)
      console.error('Error loading content suggestions:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleApproval = async (id, action) => {
    setError(null)
    
    try {
      // Update local state immediately for better UX
      setSuggestions(prev => prev.map(suggestion => 
        suggestion.id === id 
          ? { ...suggestion, status: action, updated_at: new Date().toISOString() }
          : suggestion
      ))

      // Send update to backend
      const response = await fetch(`/api/content/suggestions/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: action })
      })

      if (!response.ok) {
        // Revert local state if API call fails
        setSuggestions(prev => prev.map(suggestion => 
          suggestion.id === id 
            ? { ...suggestion, status: 'pending' }
            : suggestion
        ))
        throw new Error('Failed to update content status')
      }

      const result = await response.json()
      console.log('Status updated:', result)
    } catch (err) {
      setError(`Failed to update status: ${err.message}`)
    }
  }

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
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'thumbs_up': return 'bg-blue-100 text-blue-800'
      case 'thumbs_down': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-4 w-4" />
      case 'rejected': return <XCircle className="h-4 w-4" />
      case 'thumbs_up': return <ThumbsUp className="h-4 w-4" />
      case 'thumbs_down': return <ThumbsDown className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const filteredSuggestions = suggestions.filter(suggestion => {
    const matchesFilter = filter === 'all' || suggestion.status === filter
    const matchesSearch = searchTerm === '' || 
      suggestion.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      suggestion.platform.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const statusCounts = suggestions.reduce((acc, suggestion) => {
    acc[suggestion.status] = (acc[suggestion.status] || 0) + 1
    return acc
  }, {})

  const truncateText = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading content suggestions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Content Approval</h3>
          <p className="text-gray-600">Review and approve AI-generated content suggestions</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button onClick={loadContentSuggestions} variant="outline" size="sm">
            <Search className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{suggestions.length}</div>
            <div className="text-sm text-gray-600">Total</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-yellow-600">{statusCounts.pending || 0}</div>
            <div className="text-sm text-gray-600">Pending</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">{statusCounts.approved || 0}</div>
            <div className="text-sm text-gray-600">Approved</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">{statusCounts.thumbs_up || 0}</div>
            <div className="text-sm text-gray-600">Liked</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-red-600">{statusCounts.rejected || 0}</div>
            <div className="text-sm text-gray-600">Rejected</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <select 
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Content ({suggestions.length})</option>
            <option value="pending">Pending ({statusCounts.pending || 0})</option>
            <option value="approved">Approved ({statusCounts.approved || 0})</option>
            <option value="thumbs_up">Liked ({statusCounts.thumbs_up || 0})</option>
            <option value="thumbs_down">Disliked ({statusCounts.thumbs_down || 0})</option>
            <option value="rejected">Rejected ({statusCounts.rejected || 0})</option>
          </select>
        </div>
        
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search content or platform..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredSuggestions.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-gray-500">
              {suggestions.length === 0 ? 'No content suggestions found. Generate some content first!' : 'No content matches your current filters.'}
            </div>
          </div>
        ) : (
          filteredSuggestions.map((suggestion) => {
            const isExpanded = expandedCards.has(suggestion.id)
            const shouldTruncate = suggestion.content.length > 150
            
            return (
              <Card key={suggestion.id} className="relative hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="capitalize">
                      {suggestion.platform}
                    </Badge>
                    <Badge className={`${getStatusColor(suggestion.status)} flex items-center gap-1`}>
                      {getStatusIcon(suggestion.status)}
                      <span className="capitalize">{suggestion.status.replace('_', ' ')}</span>
                    </Badge>
                  </div>
                  {suggestion.type && (
                    <Badge variant="outline" className="w-fit">
                      {suggestion.type}
                    </Badge>
                  )}
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {shouldTruncate && !isExpanded 
                        ? truncateText(suggestion.content)
                        : suggestion.content
                      }
                    </p>
                    
                    {shouldTruncate && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleCardExpansion(suggestion.id)}
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

                  {suggestion.hashtags && (
                    <p className="text-xs text-blue-600 font-medium">
                      {suggestion.hashtags}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {suggestion.optimal_time || 'Anytime'}
                    </span>
                    <span>Score: {suggestion.engagement_score || 'N/A'}/10</span>
                  </div>

                  {/* Action Buttons - Only show for pending items */}
                  {suggestion.status === 'pending' && (
                    <div className="flex items-center space-x-2 pt-2 border-t">
                      <Button 
                        size="sm" 
                        onClick={() => handleApproval(suggestion.id, 'approved')}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle size={14} className="mr-1" />
                        Approve
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleApproval(suggestion.id, 'thumbs_up')}
                        className="border-blue-300 text-blue-600 hover:bg-blue-50"
                      >
                        <ThumbsUp size={14} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleApproval(suggestion.id, 'thumbs_down')}
                        className="border-orange-300 text-orange-600 hover:bg-orange-50"
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

                  {/* Status Change Info */}
                  {suggestion.status !== 'pending' && suggestion.updated_at && (
                    <div className="text-xs text-gray-400 pt-2 border-t">
                      Updated: {new Date(suggestion.updated_at).toLocaleString()}
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })
        )}
      </div>
    </div>
  )
}

export default EnhancedContentApproval
