export default function DataTable({
  columns,
  rows,
  isLoading = false,
  emptyMessage = 'No data available.',
  onRowClick,
}) {
  const hasRows = Array.isArray(rows) && rows.length > 0

  return (
    <div className="card">
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr className="table-row">
              <td className="table-empty" colSpan={columns.length}>Loading data...</td>
            </tr>
          )}
          {!isLoading && hasRows && rows.map((row, index) => (
            <tr
              key={row.id || index}
              className="table-row"
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              style={onRowClick ? { cursor: 'pointer' } : undefined}
            >
              {columns.map((col) => (
                <td key={col.key}>{row[col.key]}</td>
              ))}
            </tr>
          ))}
          {!isLoading && !hasRows && (
            <tr className="table-row">
              <td className="table-empty" colSpan={columns.length}>{emptyMessage}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
