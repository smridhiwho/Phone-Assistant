import { useState } from 'react'
import { Smartphone, Battery, Camera, Cpu, ChevronDown, ChevronUp, Plus, Check } from 'lucide-react'
import { Phone } from '../../types'
import { Badge } from '../ui/Badge'
import { useChatStore } from '../../store/chatStore'
import { clsx } from 'clsx'

interface ProductCardProps {
  phone: Phone;
  compact?: boolean;
}

export function ProductCard({ phone, compact = false }: ProductCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { comparePhones, addToCompare, removeFromCompare } = useChatStore()

  const isInCompare = comparePhones.some((p) => p.id === phone.id)
  const canAddToCompare = comparePhones.length < 4

  const handleCompareToggle = () => {
    if (isInCompare) {
      removeFromCompare(phone.id)
    } else if (canAddToCompare) {
      addToCompare(phone)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price)
  }

  if (compact) {
    return (
      <div className="rounded-xl border border-border bg-card p-3 hover:shadow-md transition-shadow">
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
            <Smartphone className="w-6 h-6 text-muted-foreground" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-medium text-sm truncate">
                  {phone.brand} {phone.model}
                </h3>
                <p className="text-primary font-semibold text-sm">
                  {formatPrice(phone.price_inr)}
                </p>
              </div>

              <button
                onClick={handleCompareToggle}
                disabled={!isInCompare && !canAddToCompare}
                className={clsx(
                  'p-1.5 rounded-lg transition-colors flex-shrink-0',
                  {
                    'bg-primary text-primary-foreground': isInCompare,
                    'hover:bg-secondary': !isInCompare && canAddToCompare,
                    'opacity-50 cursor-not-allowed': !isInCompare && !canAddToCompare,
                  }
                )}
                title={isInCompare ? 'Remove from compare' : 'Add to compare'}
              >
                {isInCompare ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
              </button>
            </div>

            <div className="flex flex-wrap gap-1 mt-2">
              {phone.ram_gb && (
                <span className="text-xs text-muted-foreground">
                  {phone.ram_gb}GB
                </span>
              )}
              {phone.battery_mah && (
                <span className="text-xs text-muted-foreground">
                  {phone.battery_mah}mAh
                </span>
              )}
              {phone.refresh_rate && phone.refresh_rate >= 120 && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                  {phone.refresh_rate}Hz
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-start gap-4">
          <div className="w-20 h-20 rounded-xl bg-secondary flex items-center justify-center flex-shrink-0">
            <Smartphone className="w-10 h-10 text-muted-foreground" />
          </div>

          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted-foreground">{phone.brand}</p>
                <h3 className="font-semibold">{phone.model}</h3>
                <p className="text-lg font-bold text-primary mt-1">
                  {formatPrice(phone.price_inr)}
                </p>
              </div>

              <button
                onClick={handleCompareToggle}
                disabled={!isInCompare && !canAddToCompare}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  {
                    'bg-primary text-primary-foreground': isInCompare,
                    'hover:bg-secondary': !isInCompare && canAddToCompare,
                    'opacity-50 cursor-not-allowed': !isInCompare && !canAddToCompare,
                  }
                )}
                title={isInCompare ? 'Remove from compare' : 'Add to compare'}
              >
                {isInCompare ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <Plus className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Quick Specs */}
        <div className="grid grid-cols-4 gap-2 mt-4">
          <div className="flex flex-col items-center p-2 rounded-lg bg-secondary/50">
            <Cpu className="w-4 h-4 text-muted-foreground mb-1" />
            <span className="text-xs font-medium">{phone.ram_gb}GB</span>
            <span className="text-[10px] text-muted-foreground">RAM</span>
          </div>
          <div className="flex flex-col items-center p-2 rounded-lg bg-secondary/50">
            <Battery className="w-4 h-4 text-muted-foreground mb-1" />
            <span className="text-xs font-medium">{phone.battery_mah}</span>
            <span className="text-[10px] text-muted-foreground">mAh</span>
          </div>
          <div className="flex flex-col items-center p-2 rounded-lg bg-secondary/50">
            <Camera className="w-4 h-4 text-muted-foreground mb-1" />
            <span className="text-xs font-medium">{phone.rear_camera?.split('+')[0]}</span>
            <span className="text-[10px] text-muted-foreground">Camera</span>
          </div>
          <div className="flex flex-col items-center p-2 rounded-lg bg-secondary/50">
            <Smartphone className="w-4 h-4 text-muted-foreground mb-1" />
            <span className="text-xs font-medium">{phone.display_size}"</span>
            <span className="text-[10px] text-muted-foreground">Display</span>
          </div>
        </div>

        {/* Features */}
        {phone.features && phone.features.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {phone.features.slice(0, 3).map((feature, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {feature}
              </Badge>
            ))}
            {phone.features.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{phone.features.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Highlights */}
        {phone.highlights && (
          <p className="text-xs text-muted-foreground mt-3 line-clamp-2">
            {phone.highlights}
          </p>
        )}
      </div>

      {/* Expandable Details */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2 border-t border-border flex items-center justify-center gap-1 text-xs text-muted-foreground hover:bg-secondary/50 transition-colors"
      >
        {isExpanded ? (
          <>
            <span>Less details</span>
            <ChevronUp className="w-4 h-4" />
          </>
        ) : (
          <>
            <span>More details</span>
            <ChevronDown className="w-4 h-4" />
          </>
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 border-t border-border">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2 mt-3 text-sm">
            <div>
              <dt className="text-muted-foreground text-xs">Processor</dt>
              <dd className="font-medium">{phone.processor || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Storage</dt>
              <dd className="font-medium">{phone.storage_gb}GB</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Display</dt>
              <dd className="font-medium">
                {phone.display_type} {phone.refresh_rate}Hz
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Fast Charging</dt>
              <dd className="font-medium">{phone.fast_charging_w}W</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Rear Camera</dt>
              <dd className="font-medium">{phone.rear_camera}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Front Camera</dt>
              <dd className="font-medium">{phone.front_camera}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">OS</dt>
              <dd className="font-medium">{phone.os || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground text-xs">Weight</dt>
              <dd className="font-medium">{phone.weight_g}g</dd>
            </div>
          </dl>

          {phone.colors && phone.colors.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-muted-foreground mb-1">Colors</p>
              <p className="text-sm">{phone.colors.join(', ')}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
