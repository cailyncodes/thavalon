// components/ClientProvider.tsx

'use client';

import { QueryClient, QueryClientProvider, Hydrate } from '@tanstack/react-query';
import { useState } from 'react';
import { ReactNode } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface ClientProviderProps {
  children: ReactNode;
}

const ClientProvider: React.FC<ClientProviderProps> = ({ children }) => {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <Hydrate>
        {children}
        <ToastContainer />
      </Hydrate>
    </QueryClientProvider>
  );
};

export default ClientProvider;
