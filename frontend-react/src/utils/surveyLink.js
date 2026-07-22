export function buildSurveyUrl({ origin, pilotTag, configId, appVersion, aiModelVersion, schemaId }) {
  const params = new URLSearchParams()
  if (pilotTag?.trim()) params.set('pilot_tag', pilotTag.trim())
  if (configId != null) params.set('config_id', String(configId))
  if (appVersion?.trim()) params.set('app_version', appVersion.trim())
  if (aiModelVersion?.trim()) params.set('ai_model_version', aiModelVersion.trim())
  if (schemaId) params.set('schema_id', String(schemaId))
  return `${origin}/public/survey?${params.toString()}`
}
