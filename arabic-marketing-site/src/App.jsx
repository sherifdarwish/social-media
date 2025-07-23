import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Bot, 
  Zap, 
  BarChart3, 
  Users, 
  Shield, 
  Globe, 
  Star,
  CheckCircle,
  ArrowLeft,
  Play,
  Sparkles,
  Target,
  TrendingUp,
  Clock,
  Heart,
  MessageSquare,
  Share2,
  Eye,
  Crown,
  CreditCard
} from 'lucide-react'
import './App.css'

function App() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const features = [
    {
      icon: <Bot className="h-8 w-8 text-blue-600" />,
      title: "ذكاء اصطناعي متقدم",
      description: "استخدم أحدث تقنيات الذكاء الاصطناعي لإنشاء محتوى جذاب ومتميز لجميع منصات التواصل الاجتماعي"
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-600" />,
      title: "أتمتة كاملة",
      description: "جدولة ونشر المحتوى تلقائياً عبر فيسبوك، تويتر، إنستغرام، لينكد إن وتيك توك"
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-green-600" />,
      title: "تحليلات شاملة",
      description: "تتبع الأداء والتفاعل مع تقارير مفصلة وتوصيات لتحسين استراتيجيتك"
    },
    {
      icon: <Users className="h-8 w-8 text-purple-600" />,
      title: "إدارة الفرق",
      description: "تعاون مع فريقك بسهولة مع أدوات إدارة المحتوى والموافقات"
    },
    {
      icon: <Shield className="h-8 w-8 text-red-600" />,
      title: "أمان متقدم",
      description: "حماية بيانات عملائك مع أعلى معايير الأمان والخصوصية"
    },
    {
      icon: <Globe className="h-8 w-8 text-indigo-600" />,
      title: "دعم متعدد اللغات",
      description: "إنشاء محتوى بالعربية والإنجليزية مع دعم كامل للكتابة من اليمين لليسار"
    }
  ]

  const testimonials = [
    {
      name: "أحمد محمد",
      company: "شركة التسويق الرقمي",
      text: "هذه المنصة غيرت طريقة عملنا تماماً. وفرنا 80% من الوقت المخصص لإنشاء المحتوى",
      rating: 5
    },
    {
      name: "فاطمة العلي",
      company: "متجر الأزياء الإلكتروني",
      text: "المحتوى المُنشأ بالذكاء الاصطناعي أفضل من المحتوى الذي كنا ننشئه يدوياً",
      rating: 5
    },
    {
      name: "خالد السعيد",
      company: "وكالة الإعلان",
      text: "عملاؤنا سعداء جداً بالنتائج. زاد التفاعل بنسبة 300% في شهر واحد فقط",
      rating: 5
    }
  ]

  const plans = [
    {
      name: "الخطة المجانية",
      price: "0",
      currency: "ريال",
      period: "شهرياً",
      description: "مثالية للمبتدئين والشركات الصغيرة",
      features: [
        "حتى 3 حسابات وسائل تواصل",
        "10 منشورات بالذكاء الاصطناعي شهرياً",
        "تحليلات أساسية",
        "دعم عبر البريد الإلكتروني"
      ],
      popular: false
    },
    {
      name: "الخطة الاحترافية",
      price: "75",
      currency: "ريال",
      period: "شهرياً",
      description: "للشركات المتنامية والوكالات",
      features: [
        "حسابات غير محدودة",
        "منشورات غير محدودة بالذكاء الاصطناعي",
        "تحليلات متقدمة وتقارير",
        "دعم على مدار الساعة",
        "نماذج ذكاء اصطناعي متقدمة",
        "جدولة مخصصة",
        "أدوات التعاون الجماعي",
        "تقارير بالعلامة التجارية",
        "وصول للـ API"
      ],
      popular: true
    }
  ]

  const stats = [
    { number: "10,000+", label: "عميل سعيد" },
    { number: "1M+", label: "منشور تم إنشاؤه" },
    { number: "500%", label: "زيادة في التفاعل" },
    { number: "24/7", label: "دعم فني" }
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="flex items-center space-x-2 space-x-reverse">
                <Bot className="h-8 w-8 text-blue-600" />
                <span className="text-xl font-bold text-gray-900">وكيل وسائل التواصل</span>
              </div>
            </div>
            <nav className="hidden md:flex items-center space-x-8 space-x-reverse">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors">المميزات</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition-colors">الأسعار</a>
              <a href="#testimonials" className="text-gray-700 hover:text-blue-600 transition-colors">آراء العملاء</a>
              <a href="#contact" className="text-gray-700 hover:text-blue-600 transition-colors">تواصل معنا</a>
            </nav>
            <div className="flex items-center space-x-4 space-x-reverse">
              <Button variant="outline">تسجيل الدخول</Button>
              <Button>ابدأ مجاناً</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
              <Sparkles className="h-4 w-4 ml-1" />
              جديد: دعم الذكاء الاصطناعي المتقدم
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              أتمت وسائل التواصل الاجتماعي
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> بالذكاء الاصطناعي</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              منصة شاملة لإدارة وأتمتة حساباتك على وسائل التواصل الاجتماعي. 
              أنشئ محتوى جذاب، جدول المنشورات، وتتبع الأداء - كل ذلك بقوة الذكاء الاصطناعي
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3">
                <Play className="h-5 w-5 ml-2" />
                ابدأ مجاناً الآن
              </Button>
              <Button size="lg" variant="outline" className="px-8 py-3">
                <Eye className="h-5 w-5 ml-2" />
                شاهد العرض التوضيحي
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              مميزات تجعل عملك أسهل
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              اكتشف كيف يمكن لمنصتنا أن تحول استراتيجية التسويق الرقمي لشركتك
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
                <CardHeader>
                  <div className="flex items-center space-x-3 space-x-reverse">
                    {feature.icon}
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              كيف يعمل النظام؟
            </h2>
            <p className="text-xl text-gray-600">
              ثلاث خطوات بسيطة لبدء رحلتك في التسويق الذكي
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">ربط الحسابات</h3>
              <p className="text-gray-600">اربط حساباتك على فيسبوك، تويتر، إنستغرام، لينكد إن وتيك توك بنقرة واحدة</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">إنشاء المحتوى</h3>
              <p className="text-gray-600">دع الذكاء الاصطناعي ينشئ محتوى جذاب ومناسب لكل منصة وجمهورك المستهدف</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">تتبع النتائج</h3>
              <p className="text-gray-600">راقب الأداء واحصل على تحليلات مفصلة لتحسين استراتيجيتك باستمرار</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ماذا يقول عملاؤنا؟
            </h2>
            <p className="text-xl text-gray-600">
              آراء حقيقية من عملاء حققوا نجاحاً باستخدام منصتنا
            </p>
          </div>
          <Card className="border-0 shadow-xl">
            <CardContent className="p-8">
              <div className="text-center">
                <div className="flex justify-center mb-4">
                  {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-xl text-gray-700 mb-6 leading-relaxed">
                  "{testimonials[currentTestimonial].text}"
                </blockquote>
                <div>
                  <div className="font-semibold text-gray-900">{testimonials[currentTestimonial].name}</div>
                  <div className="text-gray-600">{testimonials[currentTestimonial].company}</div>
                </div>
              </div>
            </CardContent>
          </Card>
          <div className="flex justify-center mt-6 space-x-2 space-x-reverse">
            {testimonials.map((_, index) => (
              <button
                key={index}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentTestimonial ? 'bg-blue-600' : 'bg-gray-300'
                }`}
                onClick={() => setCurrentTestimonial(index)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              خطط تناسب جميع الاحتياجات
            </h2>
            <p className="text-xl text-gray-600">
              اختر الخطة المناسبة لك وابدأ رحلتك في التسويق الذكي
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {plans.map((plan, index) => (
              <Card key={index} className={`relative ${plan.popular ? 'ring-2 ring-blue-500 shadow-xl' : 'shadow-lg'}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-600 text-white px-4 py-1">
                      <Crown className="h-4 w-4 ml-1" />
                      الأكثر شعبية
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-blue-600">{plan.price}</span>
                    <span className="text-gray-600 mr-2">{plan.currency} {plan.period}</span>
                  </div>
                  <CardDescription className="text-base">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-600 ml-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button className={`w-full ${plan.popular ? 'bg-blue-600 hover:bg-blue-700' : ''}`}>
                    {plan.price === "0" ? "ابدأ مجاناً" : "اشترك الآن"}
                    <CreditCard className="h-4 w-4 mr-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            جاهز لتحويل استراتيجية التسويق الخاصة بك؟
          </h2>
          <p className="text-xl mb-8 opacity-90">
            انضم إلى آلاف الشركات التي تستخدم منصتنا لتحقيق نتائج مذهلة في وسائل التواصل الاجتماعي
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              ابدأ تجربتك المجانية
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
              تحدث مع خبير
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 space-x-reverse mb-4">
                <Bot className="h-8 w-8 text-blue-400" />
                <span className="text-xl font-bold">وكيل وسائل التواصل</span>
              </div>
              <p className="text-gray-400 leading-relaxed">
                منصة شاملة لأتمتة وإدارة حساباتك على وسائل التواصل الاجتماعي بقوة الذكاء الاصطناعي
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">المنتج</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">المميزات</a></li>
                <li><a href="#" className="hover:text-white transition-colors">الأسعار</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="hover:text-white transition-colors">التكاملات</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">الشركة</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">من نحن</a></li>
                <li><a href="#" className="hover:text-white transition-colors">المدونة</a></li>
                <li><a href="#" className="hover:text-white transition-colors">الوظائف</a></li>
                <li><a href="#" className="hover:text-white transition-colors">اتصل بنا</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">الدعم</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">مركز المساعدة</a></li>
                <li><a href="#" className="hover:text-white transition-colors">الوثائق</a></li>
                <li><a href="#" className="hover:text-white transition-colors">حالة النظام</a></li>
                <li><a href="#" className="hover:text-white transition-colors">سياسة الخصوصية</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 وكيل وسائل التواصل. جميع الحقوق محفوظة.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
