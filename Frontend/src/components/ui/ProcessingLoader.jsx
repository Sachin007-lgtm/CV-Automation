import React from 'react';
import { Loader2 } from 'lucide-react';

const ProcessingLoader = () => (
  <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
    <div className="bg-white p-8 rounded-xl shadow-lg flex flex-col items-center">
      <Loader2 className="animate-spin w-10 h-10 text-red-500 mb-4" />
      <div className="text-lg font-semibold text-gray-700">Processing...</div>
    </div>
  </div>
);

export default ProcessingLoader;
