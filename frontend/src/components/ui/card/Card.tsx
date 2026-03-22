import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return <div className={`p-6 border-b border-gray-200 dark:border-gray-700 ${className}`} {...props}>{children}</div>;
};

export const CardTitle: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return <h3 className={`text-xl font-semibold text-gray-900 dark:text-white ${className}`} {...props}>{children}</h3>;
};

export const CardDescription: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return <p className={`text-sm text-gray-600 dark:text-gray-400 mt-1 ${className}`} {...props}>{children}</p>;
};

export const CardContent: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return <div className={`p-6 ${className}`} {...props}>{children}</div>;
};

export const CardFooter: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return <div className={`p-6 border-t border-gray-200 dark:border-gray-700 ${className}`} {...props}>{children}</div>;
};

export default Card;
