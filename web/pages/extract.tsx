import { useState } from 'react';
import { apiClient, handleApiError } from '../lib/apiClient';
import { ExtractResponse } from '../lib/types';

export default function ExtractPage() {
  const [text, setText] = useState('');
  const [data, setData] = useState<ExtractResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setData(null);
    try {
      const res = await apiClient.post<ExtractResponse>('/extract', { text });
      setData(res.data);
    } catch (err) {
      setError(await handleApiError(err));
    }
  };

  const renderHighlightedText = () => {
    if (!data) return text;
    const sortedEntities = [...data.entities].sort((a, b) => a.start - b.start);
    const result: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedEntities.forEach((ent, idx) => {
      if (ent.start > lastIndex) {
        result.push(text.slice(lastIndex, ent.start));
      }
      result.push(
        <mark key={idx} className="bg-yellow-200 px-1 rounded border border-yellow-400">
          {ent.text} <span className="text-xs font-bold text-gray-600">({ent.label})</span>
        </mark>
      );
      lastIndex = ent.end;
    });

    if (lastIndex < text.length) {
      result.push(text.slice(lastIndex));
    }
    return result;
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Entity Extraction</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full border p-2 rounded h-32"
          placeholder="Enter text to extract entities..."
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Extract
        </button>
      </form>
      {error && <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>}
      {data && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="font-semibold mb-2">Result:</h2>
          <div className="whitespace-pre-wrap leading-relaxed">{renderHighlightedText()}</div>
        </div>
      )}
    </div>
  );
}