import { Button } from '@/components/ui/button.jsx'
import { useLanguage } from './LanguageProvider.jsx'
import { Globe } from 'lucide-react'

const LanguageSwitcher = () => {
  const { language, toggleLanguage, isRTL } = useLanguage()

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLanguage}
      className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}
    >
      <Globe size={16} />
      <span className="font-medium">
        {language === 'en' ? 'العربية' : 'English'}
      </span>
    </Button>
  )
}

export default LanguageSwitcher
