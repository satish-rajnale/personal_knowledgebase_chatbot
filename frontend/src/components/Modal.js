import React, { useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  message, 
  type = 'info', // 'success', 'error', 'info', 'warning'
  showCloseButton = true,
  autoClose = false,
  autoCloseDelay = 5000,
  actions = null // Custom actions array: [{ label, onClick, variant }]
}) => {
  useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, autoCloseDelay);
      
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, autoCloseDelay, onClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-6 w-6 text-red-600" />;
      case 'warning':
        return <AlertCircle className="h-6 w-6 text-yellow-600" />;
      default:
        return <Info className="h-6 w-6 text-blue-600" />;
    }
  };

  const getBgColor = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getTitleColor = () => {
    switch (type) {
      case 'success':
        return 'text-green-900';
      case 'error':
        return 'text-red-900';
      case 'warning':
        return 'text-yellow-900';
      default:
        return 'text-blue-900';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={showCloseButton ? onClose : undefined}
        />
        
        {/* Modal */}
        <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
          <div className={`px-4 py-3 sm:p-6 ${getBgColor()} border-l-4`}>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {getIcon()}
              </div>
              <div className="ml-3 w-0 flex-1">
                <h3 className={`text-lg font-medium ${getTitleColor()}`}>
                  {title}
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-700 whitespace-pre-line">
                    {message}
                  </p>
                </div>
              </div>
              {showCloseButton && (
                <div className="ml-auto flex flex-shrink-0">
                  <button
                    type="button"
                    className="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <X className="h-5 w-5" />
                  </button>
                </div>
              )}
            </div>
          </div>
          
          {/* Action buttons */}
          <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
            {actions ? (
              <>
                {actions.map((action, index) => (
                  <button
                    key={index}
                    type="button"
                    className={`inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold shadow-sm sm:ml-3 sm:w-auto ${
                      action.variant === 'secondary' 
                        ? 'bg-gray-300 text-gray-700 hover:bg-gray-400' 
                        : action.variant === 'danger'
                        ? 'bg-red-600 text-white hover:bg-red-500'
                        : type === 'success' ? 'bg-green-600 hover:bg-green-500 text-white' :
                          type === 'error' ? 'bg-red-600 hover:bg-red-500 text-white' :
                          type === 'warning' ? 'bg-yellow-600 hover:bg-yellow-500 text-white' :
                          'bg-blue-600 hover:bg-blue-500 text-white'
                    }`}
                    onClick={action.onClick}
                  >
                    {action.label}
                  </button>
                ))}
              </>
            ) : (
              <button
                type="button"
                className={`inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white shadow-sm sm:ml-3 sm:w-auto ${
                  type === 'success' ? 'bg-green-600 hover:bg-green-500' :
                  type === 'error' ? 'bg-red-600 hover:bg-red-500' :
                  type === 'warning' ? 'bg-yellow-600 hover:bg-yellow-500' :
                  'bg-blue-600 hover:bg-blue-500'
                }`}
                onClick={onClose}
              >
                OK
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal; 