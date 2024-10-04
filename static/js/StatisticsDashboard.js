const { useState, useEffect } = React;

function ArrowUpIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5"></line>
      <polyline points="5 12 12 5 19 12"></polyline>
    </svg>
  );
}

function ArrowDownIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"></line>
      <polyline points="19 12 12 19 5 12"></polyline>
    </svg>
  );
}

function StatisticsDashboard() {
  const [statistics, setStatistics] = useState([]);

  useEffect(() => {
    fetch('/stats')
      .then(response => response.json())
      .then(data => {
        const stats = Object.entries(data).map(([name, value]) => ({
          name,
          currentValue: value,
          previousValue: value // For now, we'll use the same value for both current and previous
        }));
        setStatistics(stats);
      })
      .catch(error => console.error('Error:', error));
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Battle Statistics Dashboard</h2>
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Statistic</th>
            <th className="py-2 px-4 border-b">Current Value</th>
            <th className="py-2 px-4 border-b">Change Since Last Update</th>
          </tr>
        </thead>
        <tbody>
          {statistics.map((stat) => {
            const change = stat.currentValue - stat.previousValue;
            const isPositive = change > 0;
            const isNeutral = change === 0;

            return (
              <tr key={stat.name}>
                <td className="py-2 px-4 border-b font-medium">{stat.name}</td>
                <td className="py-2 px-4 border-b">{stat.currentValue}</td>
                <td className="py-2 px-4 border-b">
                  <span className={`flex items-center ${isPositive ? 'text-green-600' : isNeutral ? 'text-gray-500' : 'text-red-600'}`}>
                    {isPositive ? (
                      <ArrowUpIcon />
                    ) : isNeutral ? (
                      <span className="w-4 h-4 mr-1">-</span>
                    ) : (
                      <ArrowDownIcon />
                    )}
                    {Math.abs(change)}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

ReactDOM.render(<StatisticsDashboard />, document.getElementById('react-stats-dashboard'));
