import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  PlusCircle, 
  Lightbulb, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  Save,
  RefreshCw
} from 'lucide-react'

const EnhancedGeneratorInterface = () => {
  const [activeStep, setActiveStep] = useState('profile')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [generatedContent, setGeneratedContent] = useState([])
  
  const [businessProfile, setBusinessProfile] = useState({
    company_name: '',
    industry: '',
    target_audience: '',
    brand_voice: 'professional'
  })

  const [contentStrategy, setContentStrategy] = useState({
    platforms: [],
    content_types: [],
    posting_frequency: 'daily',
    campaign_name: ''
  })

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Validate required fields
      if (!businessProfile.company_name || !businessProfile.industry) {
        throw new Error('Company name and industry are required')
      }

      // Save business profile
      const response = await fetch('/api/generator/business-brief', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(businessProfile)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to save business profile')
      }

      setSuccess('Business profile saved successfully!')
      setActiveStep('strategy')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStrategySubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Validate strategy
      if (contentStrategy.platforms.length === 0) {
        throw new Error('Please select at least one platform')
      }

      if (!contentStrategy.campaign_name) {
        throw new Error('Campaign name is required')
      }

      setSuccess('Content strategy configured successfully!')
      setActiveStep('generate')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const generateContentSuggestions = async () => {
    setError(null)
    setLoading(true)
    setGeneratedContent([])

    try {
      const response = await fetch('/api/content/suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          business_profile: businessProfile,
          content_strategy: contentStrategy
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to generate content suggestions')
      }

      const data = await response.json()
      setGeneratedContent(data.suggestions || [])
      setSuccess(`Generated ${data.suggestions?.length || 0} content suggestions successfully!`)
    } catch (err) {
      setError(err.message)
      console.error('Content generation error:', err)
    } finally {
      setLoading(false)
    }
  }

  const saveContentSuggestions = async () => {
    if (generatedContent.length === 0) {
      setError('No content to save')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/content/save-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          suggestions: generatedContent,
          campaign_name: contentStrategy.campaign_name
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to save content suggestions')
      }

      setSuccess('Content suggestions saved successfully!')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-semibold">Content Generator</h3>
          <p className="text-gray-600">Create AI-powered content for your social media platforms</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          <RefreshCw size={16} className="mr-2" />
          Reset
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Alert */}
      {success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

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
                    <label className="block text-sm font-medium mb-2">Company Name *</label>
                    <input
                      type="text"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={businessProfile.company_name}
                      onChange={(e) => setBusinessProfile(prev => ({
                        ...prev,
                        company_name: e.target.value
                      }))}
                      placeholder="Enter your company name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Industry *</label>
                    <select
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={businessProfile.industry}
                      onChange={(e) => setBusinessProfile(prev => ({
                        ...prev,
                        industry: e.target.value
                      }))}
                    >
                      <option value="">Select industry</option>
                      <option value="technology">Technology</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="finance">Finance</option>
                      <option value="retail">Retail</option>
                      <option value="education">Education</option>
                      <option value="food">Food & Beverage</option>
                      <option value="travel">Travel & Tourism</option>
                      <option value="real-estate">Real Estate</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Target Audience</label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    value={businessProfile.target_audience}
                    onChange={(e) => setBusinessProfile(prev => ({
                      ...prev,
                      target_audience: e.target.value
                    }))}
                    placeholder="Describe your target audience (age, interests, demographics)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Brand Voice</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={businessProfile.brand_voice}
                    onChange={(e) => setBusinessProfile(prev => ({
                      ...prev,
                      brand_voice: e.target.value
                    }))}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="playful">Playful</option>
                  </select>
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving Profile...
                    </>
                  ) : (
                    <>
                      <Save size={16} className="mr-2" />
                      Save Profile & Continue
                    </>
                  )}
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
                Configure your content strategy and platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleStrategySubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Campaign Name *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={contentStrategy.campaign_name}
                    onChange={(e) => setContentStrategy(prev => ({
                      ...prev,
                      campaign_name: e.target.value
                    }))}
                    placeholder="Enter campaign name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Select Platforms *</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok'].map(platform => (
                      <label key={platform} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={contentStrategy.platforms.includes(platform)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setContentStrategy(prev => ({
                                ...prev,
                                platforms: [...prev.platforms, platform]
                              }))
                            } else {
                              setContentStrategy(prev => ({
                                ...prev,
                                platforms: prev.platforms.filter(p => p !== platform)
                              }))
                            }
                          }}
                        />
                        <span className="capitalize">{platform}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Content Types</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {['promotional', 'educational', 'entertaining', 'news', 'behind-the-scenes'].map(type => (
                      <label key={type} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={contentStrategy.content_types.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setContentStrategy(prev => ({
                                ...prev,
                                content_types: [...prev.content_types, type]
                              }))
                            } else {
                              setContentStrategy(prev => ({
                                ...prev,
                                content_types: prev.content_types.filter(t => t !== type)
                              }))
                            }
                          }}
                        />
                        <span className="capitalize">{type.replace('-', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Configuring Strategy...
                    </>
                  ) : (
                    'Configure Strategy & Continue'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generate" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Generate Content</CardTitle>
              <CardDescription>
                Generate AI-powered content suggestions based on your profile and strategy
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-4">
                <Button 
                  onClick={generateContentSuggestions} 
                  className="flex-1"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Content...
                    </>
                  ) : (
                    <>
                      <Lightbulb size={16} className="mr-2" />
                      Generate Content Suggestions
                    </>
                  )}
                </Button>
                {generatedContent.length > 0 && (
                  <Button 
                    onClick={saveContentSuggestions}
                    variant="outline"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save size={16} className="mr-2" />
                        Save All
                      </>
                    )}
                  </Button>
                )}
              </div>

              {/* Generated Content Display */}
              {generatedContent.length > 0 && (
                <div className="space-y-4">
                  <h4 className="font-medium">Generated Content ({generatedContent.length} suggestions)</h4>
                  <div className="grid gap-4">
                    {generatedContent.map((content, index) => (
                      <Card key={index} className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-2">
                          <div className="flex items-center justify-between">
                            <Badge variant="secondary">{content.platform}</Badge>
                            <Badge variant="outline">{content.type}</Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-gray-700 mb-2">{content.content}</p>
                          {content.hashtags && (
                            <p className="text-xs text-blue-600">{content.hashtags}</p>
                          )}
                          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                            <span>Engagement Score: {content.engagement_score}/10</span>
                            <span>Best Time: {content.optimal_time}</span>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default EnhancedGeneratorInterface
