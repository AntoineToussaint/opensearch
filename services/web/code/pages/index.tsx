import Layout from '../components/layout';
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';

const SearchComponent = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchResults = useCallback(
        debounce(async (searchQuery) => {
            if (searchQuery.length < 2) {
                setResults([]);
                return;
            }

            setLoading(true);
            setError(null);
            try {
                const response = await axios.get(`http://localhost:53432/search?q=${searchQuery}&fields=briefTitle&fields=conditions&page=1&size=10`);
                setResults(response.data);
            } catch (err) {
                setError('An error occurred while fetching results. Please try again.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        }, 300),
        []
    );

    useEffect(() => {
        fetchResults(query);
    }, [query, fetchResults]);

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div className="mb-4 relative">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search clinical trials..."
                    className="w-full p-2 border rounded"
                />
                {loading && (
                    <div className="absolute right-3 top-2">
                        <svg className="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                )}
            </div>

            {error && <p className="text-red-500 mb-4">{error}</p>}

            {results.length > 0 && (
                <ul className="space-y-4">
                    {results.slice(0, 10).map((trial) => (
                        <li key={trial.nctId} className="border p-4 rounded shadow-sm hover:shadow-md transition-shadow duration-200">
                            <h3 className="font-bold text-lg">{trial.briefTitle}</h3>
                            <p className="text-sm text-gray-600">NCT ID: {trial.nctId}</p>
                            <p className="text-sm">Status: {trial.overallStatus}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default function Home() {
    return (
        <Layout>
            <div className="grid gap-[30px] items-center justify-center mt-40">
                <h1 className="text-2xl font-bold text-center">Clinical Trials Search</h1>
                <SearchComponent />
            </div>
        </Layout>
    );
}
