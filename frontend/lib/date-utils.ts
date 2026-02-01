/**
 * Utility functions for timestamp formatting
 */

export const formatDate = (dateString: string | Date): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    })
  } catch (e) {
    return String(dateString)
  }
}

export const formatDateShort = (dateString: string | Date): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    })
  } catch (e) {
    return String(dateString)
  }
}

export const formatTime = (dateString: string | Date): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid time'
    }
    
    return date.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    })
  } catch (e) {
    return String(dateString)
  }
}

export const getRelativeTime = (dateString: string | Date): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (seconds < 60) return 'just now'
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    if (days < 7) return `${days}d ago`
    
    return formatDateShort(date)
  } catch (e) {
    return String(dateString)
  }
}
