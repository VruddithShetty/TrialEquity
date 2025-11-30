'use client'

import { useToast } from '@/hooks/use-toast'

export function Toaster() {
  const { toasts } = useToast()
  return (
    <div className="fixed bottom-0 right-0 z-[100] flex flex-col-reverse p-4 sm:flex-col">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="mb-4 rounded-lg bg-white p-4 shadow-lg border"
        >
          {toast.title && <div className="font-semibold">{toast.title}</div>}
          {toast.description && <div className="text-sm text-gray-600">{toast.description}</div>}
        </div>
      ))}
    </div>
  )
}

