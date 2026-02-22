import { useState } from 'react'
import { useApi } from '../api/hooks.js'
import { apiRequest } from '../api/client'

export default function ModuleCategoryPanel({ moduleKey, title }) {
  const [formState, setFormState] = useState({ name: '', description: '', sortOrder: 0 })
  const [message, setMessage] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  const { data, reload } = useApi(
    `/organizations/module-categories/?module=${moduleKey}&page_size=200&ordering=sort_order`
  )

  const categories = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []

  const handleChange = (field) => (event) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    if (isSaving) {
      return
    }
    setIsSaving(true)
    setMessage('')
    try {
      await apiRequest('/organizations/module-categories/', {
        method: 'POST',
        body: {
          module: moduleKey,
          name: formState.name.trim(),
          description: formState.description.trim(),
          sort_order: Number(formState.sortOrder),
          is_active: true,
        },
      })
      setFormState({ name: '', description: '', sortOrder: 0 })
      reload()
      setMessage('Category added.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    } finally {
      setIsSaving(false)
    }
  }

  const toggleActive = async (category) => {
    setMessage('')
    try {
      await apiRequest(`/organizations/module-categories/${category.id}/`, {
        method: 'PATCH',
        body: { is_active: !category.is_active },
      })
      reload()
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleDelete = async (categoryId) => {
    setMessage('')
    try {
      await apiRequest(`/organizations/module-categories/${categoryId}/`, { method: 'DELETE' })
      reload()
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  return (
    <div className="card">
      <h3>{title}</h3>
      {message ? <div className="banner" style={{ marginBottom: '1rem' }}>{message}</div> : null}
      <form className="form-grid" onSubmit={handleCreate}>
        <div className="form-field">
          <label>Name</label>
          <input value={formState.name} onChange={handleChange('name')} required />
        </div>
        <div className="form-field">
          <label>Description</label>
          <input value={formState.description} onChange={handleChange('description')} />
        </div>
        <div className="form-field">
          <label>Sort order</label>
          <input type="number" value={formState.sortOrder} onChange={handleChange('sortOrder')} />
        </div>
        <div className="form-field">
          <button type="submit" disabled={isSaving}>{isSaving ? 'Saving...' : 'Add Category'}</button>
        </div>
      </form>

      <table className="table" style={{ marginTop: '1rem' }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Active</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {categories.length === 0 ? (
            <tr>
              <td colSpan="4" className="table-empty">No categories yet.</td>
            </tr>
          ) : categories.map((category) => (
            <tr key={category.id}>
              <td>{category.name}</td>
              <td>{category.description || '-'}</td>
              <td>
                <button type="button" className="ghost" onClick={() => toggleActive(category)}>
                  {category.is_active ? 'Active' : 'Inactive'}
                </button>
              </td>
              <td>
                <button type="button" className="ghost" onClick={() => handleDelete(category.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
