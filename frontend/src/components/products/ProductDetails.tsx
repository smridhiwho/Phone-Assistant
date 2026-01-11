import {
  Smartphone,
  Battery,
  Camera,
  Cpu,
  HardDrive,
  Monitor,
  Zap,
  Wifi,
  X,
} from 'lucide-react'
import { Phone } from '../../types'
import { Badge } from '../ui/Badge'

interface ProductDetailsProps {
  phone: Phone;
  onClose?: () => void;
}

export function ProductDetails({ phone, onClose }: ProductDetailsProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price)
  }

  const specs = [
    {
      icon: Monitor,
      label: 'Display',
      value: `${phone.display_size}" ${phone.display_type || ''} ${phone.refresh_rate || 60}Hz`,
    },
    {
      icon: Cpu,
      label: 'Processor',
      value: phone.processor || 'N/A',
    },
    {
      icon: HardDrive,
      label: 'Memory',
      value: `${phone.ram_gb}GB RAM / ${phone.storage_gb}GB Storage`,
    },
    {
      icon: Camera,
      label: 'Rear Camera',
      value: phone.rear_camera || 'N/A',
    },
    {
      icon: Camera,
      label: 'Front Camera',
      value: phone.front_camera || 'N/A',
    },
    {
      icon: Battery,
      label: 'Battery',
      value: `${phone.battery_mah}mAh`,
    },
    {
      icon: Zap,
      label: 'Charging',
      value: `${phone.fast_charging_w}W Fast Charging${phone.wireless_charging ? ' + Wireless' : ''}`,
    },
    {
      icon: Wifi,
      label: 'Connectivity',
      value: phone.features?.includes('5G') ? '5G' : '4G LTE',
    },
  ]

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      {/* Header */}
      <div className="p-6 bg-secondary/30">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-24 h-24 rounded-xl bg-secondary flex items-center justify-center">
              <Smartphone className="w-12 h-12 text-muted-foreground" />
            </div>

            <div>
              <p className="text-sm text-muted-foreground">{phone.brand}</p>
              <h2 className="text-xl font-bold">{phone.model}</h2>
              <p className="text-2xl font-bold text-primary mt-2">
                {formatPrice(phone.price_inr)}
              </p>

              {phone.highlights && (
                <p className="text-sm text-muted-foreground mt-2 max-w-md">
                  {phone.highlights}
                </p>
              )}
            </div>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Features */}
        {phone.features && phone.features.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {phone.features.map((feature, index) => (
              <Badge key={index} variant="secondary">
                {feature}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Specifications */}
      <div className="p-6">
        <h3 className="font-semibold mb-4">Specifications</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {specs.map((spec) => (
            <div
              key={spec.label}
              className="flex items-start gap-3 p-3 rounded-lg bg-secondary/30"
            >
              <spec.icon className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-muted-foreground">{spec.label}</p>
                <p className="font-medium">{spec.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-xs text-muted-foreground">OS</p>
            <p className="font-medium text-sm">{phone.os || 'N/A'}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-xs text-muted-foreground">Dimensions</p>
            <p className="font-medium text-sm">{phone.dimensions || 'N/A'}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-xs text-muted-foreground">Weight</p>
            <p className="font-medium text-sm">{phone.weight_g}g</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-xs text-muted-foreground">Launch Year</p>
            <p className="font-medium text-sm">{phone.launch_year || 'N/A'}</p>
          </div>
        </div>

        {/* Colors */}
        {phone.colors && phone.colors.length > 0 && (
          <div className="mt-6">
            <p className="text-sm text-muted-foreground mb-2">Available Colors</p>
            <div className="flex flex-wrap gap-2">
              {phone.colors.map((color, index) => (
                <span
                  key={index}
                  className="px-3 py-1 rounded-full bg-secondary text-sm"
                >
                  {color}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
