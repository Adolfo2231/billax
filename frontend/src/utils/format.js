// Utilidades de formato y helpers para cuentas y transacciones

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(amount || 0);
}

export function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

export function getAccountIcon(type) {
  switch (type?.toLowerCase()) {
    case 'depository': return '🏦';
    case 'credit': return '💳';
    case 'loan': return '💰';
    case 'investment': return '📈';
    default: return '🏛️';
  }
} 