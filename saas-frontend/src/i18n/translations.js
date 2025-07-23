export const translations = {
  en: {
    // Navigation
    dashboard: "Dashboard",
    generator: "Content Generator", 
    approval: "Content Approval",
    campaigns: "Campaigns",
    analytics: "Analytics",
    settings: "Settings",
    
    // Dashboard
    activeCampaigns: "Active Campaigns",
    contentGenerated: "Content Generated",
    approvalRate: "Approval Rate",
    engagementScore: "Engagement Score",
    recentActivity: "Recent Activity",
    
    // Campaigns
    createCampaign: "Create Campaign",
    campaignName: "Campaign Name",
    platforms: "Platforms",
    postsGenerated: "Posts Generated",
    postsScheduled: "Posts Scheduled",
    engagement: "Engagement",
    reach: "Reach",
    
    // Settings
    agentConfiguration: "Agent Configuration",
    socialMedia: "Social Media",
    apiKeys: "API Keys",
    account: "Account",
    billing: "Billing",
    
    // Subscription Plans
    freePlan: "Free Plan",
    proPlan: "Pro Plan",
    currentPlan: "Current Plan",
    upgradeToPro: "Upgrade to Pro",
    securePayments: "Secure Payments",
    instantActivation: "Instant Activation",
    cancelAnytime: "Cancel Anytime",
    
    // Common
    save: "Save",
    cancel: "Cancel",
    edit: "Edit",
    delete: "Delete",
    create: "Create",
    update: "Update",
    loading: "Loading...",
    success: "Success",
    error: "Error"
  },
  ar: {
    // Navigation
    dashboard: "لوحة التحكم",
    generator: "منشئ المحتوى",
    approval: "موافقة المحتوى", 
    campaigns: "الحملات",
    analytics: "التحليلات",
    settings: "الإعدادات",
    
    // Dashboard
    activeCampaigns: "الحملات النشطة",
    contentGenerated: "المحتوى المُنشأ",
    approvalRate: "معدل الموافقة",
    engagementScore: "نقاط التفاعل",
    recentActivity: "النشاط الأخير",
    
    // Campaigns
    createCampaign: "إنشاء حملة",
    campaignName: "اسم الحملة",
    platforms: "المنصات",
    postsGenerated: "المنشورات المُنشأة",
    postsScheduled: "المنشورات المجدولة",
    engagement: "التفاعل",
    reach: "الوصول",
    
    // Settings
    agentConfiguration: "إعداد الوكلاء",
    socialMedia: "وسائل التواصل الاجتماعي",
    apiKeys: "مفاتيح API",
    account: "الحساب",
    billing: "الفوترة",
    
    // Subscription Plans
    freePlan: "الخطة المجانية",
    proPlan: "الخطة الاحترافية",
    currentPlan: "الخطة الحالية",
    upgradeToPro: "ترقية للاحترافية",
    securePayments: "مدفوعات آمنة",
    instantActivation: "تفعيل فوري",
    cancelAnytime: "إلغاء في أي وقت",
    
    // Common
    save: "حفظ",
    cancel: "إلغاء",
    edit: "تعديل",
    delete: "حذف",
    create: "إنشاء",
    update: "تحديث",
    loading: "جاري التحميل...",
    success: "نجح",
    error: "خطأ"
  }
}

export const useTranslation = (language = 'en') => {
  const t = (key) => {
    return translations[language]?.[key] || translations.en[key] || key
  }
  
  return { t }
}
