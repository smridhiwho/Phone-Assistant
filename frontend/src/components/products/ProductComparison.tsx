import { X, Trophy } from 'lucide-react'
import { Phone, ComparisonSpec } from '../../types'
import { useChatStore } from '../../store/chatStore'
import { Badge } from '../ui/Badge'

interface ProductComparisonProps {
  phones: Phone[];
  comparison: ComparisonSpec[];
  summary?: string;
}

export function ProductComparison({
  phones,
  comparison,
  summary,
}: ProductComparisonProps) {
  const { removeFromCompare, clearCompare } = useChatStore()

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price)
  }

  if (phones.length < 2) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Select at least 2 phones to compare
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Comparison</h3>
        <button
          onClick={clearCompare}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          Clear all
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="p-4 rounded-xl bg-secondary/50 text-sm">
          {summary}
        </div>
      )}

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-3 font-medium text-muted-foreground">
                Specification
              </th>
              {phones.map((phone) => (
                <th key={phone.id} className="p-3 text-center">
                  <div className="flex flex-col items-center gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">
                        {phone.brand} {phone.model}
                      </span>
                      <button
                        onClick={() => removeFromCompare(phone.id)}
                        className="p-1 hover:bg-secondary rounded"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                    <span className="text-primary font-bold">
                      {formatPrice(phone.price_inr)}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.map((spec) => (
              <tr key={spec.spec_name} className="border-b border-border">
                <td className="p-3 font-medium">{spec.spec_name}</td>
                {phones.map((phone) => {
                  const value = spec.values[String(phone.id)]
                  const isWinner = spec.winner === String(phone.id)

                  return (
                    <td
                      key={phone.id}
                      className="p-3 text-center"
                    >
                      <div className="flex items-center justify-center gap-1">
                        <span className={isWinner ? 'font-semibold text-primary' : ''}>
                          {value || 'N/A'}
                        </span>
                        {isWinner && (
                          <Trophy className="w-4 h-4 text-yellow-500" />
                        )}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Feature Comparison */}
      <div>
        <h4 className="font-medium mb-2">Features</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {phones.map((phone) => (
            <div
              key={phone.id}
              className="p-3 rounded-xl border border-border"
            >
              <p className="font-medium text-sm mb-2">
                {phone.brand} {phone.model}
              </p>
              <div className="flex flex-wrap gap-1">
                {phone.features?.map((feature, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">
                    {feature}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
