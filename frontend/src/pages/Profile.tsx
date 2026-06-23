import { useState, type FormEvent } from 'react'
import { useAuth } from '../context/AuthContext'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'

export default function Profile() {
  const { user, updateProfile } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [college, setCollege] = useState(user?.college ?? '')
  const [branch, setBranch] = useState(user?.branch ?? '')
  const [gradYear, setGradYear] = useState(user?.graduation_year?.toString() ?? '')
  const [targets, setTargets] = useState(user?.target_companies?.join(', ') ?? '')
  const [leetcodeUsername, setLeetcodeUsername] = useState(
    user?.leetcode_username ?? 'soumyapoddar16'
  )
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')
    try {
      await updateProfile({
        full_name: fullName,
        college: college || undefined,
        branch: branch || undefined,
        graduation_year: gradYear ? parseInt(gradYear, 10) : undefined,
        target_companies: targets
          ? targets.split(',').map((s) => s.trim()).filter(Boolean)
          : undefined,
        leetcode_username: leetcodeUsername.trim() || undefined,
      } as Parameters<typeof updateProfile>[0])
      setMessage('Profile updated successfully')
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Update failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PageHeader title="Profile" subtitle="Manage your account and placement targets" />

      <Card className="max-w-xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Email" value={user?.email ?? ''} disabled />
          <Field label="Full Name" value={fullName} onChange={setFullName} />
          <Field label="College" value={college} onChange={setCollege} />
          <Field label="Branch" value={branch} onChange={setBranch} />
          <Field label="Graduation Year" value={gradYear} onChange={setGradYear} type="number" />
          <div>
            <label className="mb-1 block text-sm font-medium">LeetCode Username</label>
            <input
              value={leetcodeUsername}
              onChange={(e) => setLeetcodeUsername(e.target.value)}
              placeholder="soumyapoddar16"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
            />
            <p className="mt-1 text-xs text-slate-400">Used for auto-sync on DSA Tracker</p>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Target Companies</label>
            <input
              value={targets}
              onChange={(e) => setTargets(e.target.value)}
              placeholder="Google, Amazon, Microsoft"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
            />
            <p className="mt-1 text-xs text-slate-400">Comma-separated company names</p>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:bg-primary-light disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
          {message && (
            <p className={`text-sm ${message.includes('success') ? 'text-emerald-600' : 'text-red-600'}`}>
              {message}
            </p>
          )}
        </form>
      </Card>
    </div>
  )
}

function Field({
  label,
  value,
  onChange,
  disabled,
  type = 'text',
}: {
  label: string
  value: string
  onChange?: (v: string) => void
  disabled?: boolean
  type?: string
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium">{label}</label>
      <input
        type={type}
        value={value}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        disabled={disabled}
        className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none disabled:bg-slate-50"
      />
    </div>
  )
}