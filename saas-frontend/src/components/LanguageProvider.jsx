import { createContext, useContext, useState, useEffect } from 'react'
import { useTranslation } from '../i18n/translations.js'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'en'
  })
  
  const { t } = useTranslation(language)
  const isRTL = language === 'ar'

  useEffect(() => {
    localStorage.setItem('language', language)
    
    // Update document direction and language
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
    document.documentElement.lang = language
    
    // Update body class for RTL styling
    if (isRTL) {
      document.body.classList.add('rtl')
    } else {
      document.body.classList.remove('rtl')
    }
  }, [language, isRTL])

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'ar' : 'en')
  }

  const value = {
    language,
    setLanguage,
    toggleLanguage,
    t,
    isRTL
  }

  return (
    <LanguageContext.Provider value={value}>
      <div className={`${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
        {children}
      </div>
    </LanguageContext.Provider>
  )
}
