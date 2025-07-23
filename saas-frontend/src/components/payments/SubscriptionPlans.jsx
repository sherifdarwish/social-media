import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Check,
  Crown,
  Zap,
  Users,
  BarChart3,
  Shield,
  CreditCard,
  Star
} from 'lucide-react'

const SubscriptionPlans = ({ currentPlan = 'free', onUpgrade }) => {
  const [selectedPlan, setSelectedPlan] = useState(currentPlan)
  const [isProcessing, setIsProcessing] = useState(false)

  const plans = [
    {
      id: 'free',
      name: 'Free Plan',
      price: 0,
      currency: 'USD',
      interval: 'month',
      description: 'Perfect for getting started with social media automation',
      features: [
        'Up to 3 social media accounts',
        '10 AI-generated posts per month',
        'Basic analytics dashboard',
        'Email support',
        'Content approval workflow'
      ],
      limitations: [
        'Limited to 3 platforms',
        'Basic AI models only',
        'Standard support'
      ],
      popular: false,
      color: 'gray'
    },
    {
      id: 'pro',
      name: 'Pro Plan',
      price: 20,
      currency: 'USD',
      interval: 'month',
      description: 'Advanced features for growing businesses and agencies',
      features: [
        'Unlimited social media accounts',
        'Unlimited AI-generated posts',
        'Advanced analytics & reporting',
        'Priority support (24/7)',
        'Advanced AI models (GPT-4, Claude)',
        'Custom posting schedules',
        'Team collaboration tools',
        'White-label reporting',
        'API access',
        'Advanced error tracking'
      ],
      limitations: [],
      popular: true,
      color: 'blue'
    }
  ]

  const handleUpgrade = async (planId) => {
    if (planId === currentPlan) return
    
    setIsProcessing(true)
    setSelectedPlan(planId)

    try {
      if (planId === 'pro') {
        // Simulate Stripe checkout
        const response = await fetch('/api/payments/create-checkout-session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            plan_id: planId,
            success_url: `${window.location.origin}/dashboard?payment=success`,
            cancel_url: `${window.location.origin}/settings?payment=cancelled`
          })
        })

        const data = await response.json()
        
        if (data.checkout_url) {
          // Redirect to Stripe Checkout
          window.location.href = data.checkout_url
        } else {
          throw new Error('Failed to create checkout session')
        }
      } else if (planId === 'free') {
        // Downgrade to free plan
        const response = await fetch('/api/payments/cancel-subscription', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })

        if (response.ok) {
          onUpgrade && onUpgrade('free')
        }
      }
    } catch (error) {
      console.error('Payment error:', error)
      alert('Payment processing failed. Please try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  const getPlanColor = (color) => {
    const colors = {
      gray: 'border-gray-200 bg-gray-50',
      blue: 'border-blue-200 bg-blue-50 ring-2 ring-blue-500'
    }
    return colors[color] || colors.gray
  }

  const getButtonVariant = (planId) => {
    if (planId === currentPlan) return 'outline'
    if (planId === 'pro') return 'default'
    return 'outline'
  }

  const getButtonText = (planId) => {
    if (planId === currentPlan) return 'Current Plan'
    if (planId === 'pro') return 'Upgrade to Pro'
    return 'Downgrade to Free'
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-gray-600 text-lg">
          Select the perfect plan for your social media automation needs
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {plans.map((plan) => (
          <Card key={plan.id} className={`relative ${getPlanColor(plan.color)}`}>
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-blue-600 text-white px-4 py-1">
                  <Star size={14} className="mr-1" />
                  Most Popular
                </Badge>
              </div>
            )}
            
            <CardHeader className="text-center pb-4">
              <div className="flex justify-center mb-4">
                {plan.id === 'free' ? (
                  <Users className="h-12 w-12 text-gray-600" />
                ) : (
                  <Crown className="h-12 w-12 text-blue-600" />
                )}
              </div>
              
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <CardDescription className="text-base">{plan.description}</CardDescription>
              
              <div className="mt-4">
                <div className="flex items-baseline justify-center">
                  <span className="text-4xl font-bold">
                    ${plan.price}
                  </span>
                  <span className="text-gray-600 ml-2">/{plan.interval}</span>
                </div>
                {plan.price === 0 && (
                  <p className="text-sm text-gray-500 mt-1">Forever free</p>
                )}
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              <div>
                <h4 className="font-semibold mb-3 flex items-center">
                  <Check className="h-4 w-4 text-green-600 mr-2" />
                  What's included:
                </h4>
                <ul className="space-y-2">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {plan.limitations.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 text-gray-600">Limitations:</h4>
                  <ul className="space-y-2">
                    {plan.limitations.map((limitation, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-gray-400 mr-2">•</span>
                        <span className="text-sm text-gray-600">{limitation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <Button
                className="w-full"
                variant={getButtonVariant(plan.id)}
                onClick={() => handleUpgrade(plan.id)}
                disabled={isProcessing || plan.id === currentPlan}
              >
                {isProcessing && selectedPlan === plan.id ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </div>
                ) : (
                  <>
                    {plan.id === 'pro' && <CreditCard className="h-4 w-4 mr-2" />}
                    {getButtonText(plan.id)}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6 text-center">
            <Shield className="h-8 w-8 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Secure Payments</h3>
            <p className="text-sm text-gray-600">
              All payments are processed securely through Stripe with industry-standard encryption
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <Zap className="h-8 w-8 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Instant Activation</h3>
            <p className="text-sm text-gray-600">
              Your plan is activated immediately after successful payment
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <BarChart3 className="h-8 w-8 text-purple-600 mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Cancel Anytime</h3>
            <p className="text-sm text-gray-600">
              No long-term contracts. Cancel or change your plan anytime
            </p>
          </CardContent>
        </Card>
      </div>

      <Alert>
        <CreditCard className="h-4 w-4" />
        <AlertDescription>
          <strong>Payment Methods:</strong> We accept all major credit cards (Visa, Mastercard, American Express) 
          and digital wallets through Stripe. Your billing information is never stored on our servers.
        </AlertDescription>
      </Alert>
    </div>
  )
}

export default SubscriptionPlans
