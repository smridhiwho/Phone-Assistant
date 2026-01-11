import { Phone } from '../../types'
import { ProductCard } from './ProductCard'
import { ProductCardSkeleton } from '../ui/Skeleton'

interface ProductGridProps {
  phones: Phone[];
  loading?: boolean;
  compact?: boolean;
}

export function ProductGrid({ phones, loading, compact }: ProductGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (phones.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No phones found matching your criteria.
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {phones.map((phone) => (
        <ProductCard key={phone.id} phone={phone} compact={compact} />
      ))}
    </div>
  )
}
