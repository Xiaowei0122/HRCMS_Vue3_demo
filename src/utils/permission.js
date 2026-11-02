import { getUserInfo } from './auth'

/**
 * 当前用户拥有的权限 code 集合。
 * 超级管理员返回 ['*'] 表示拥有全部权限（与后端 require_permission 的放行语义一致）。
 */
export function getPermissions() {
  const info = getUserInfo()
  if (!info) return []
  if (info.roleCode === 'super_admin') return ['*']
  return info.permissions || []
}

/**
 * 是否拥有任一指定权限 code。
 * 用法：hasPerm('repair:create') 或 hasPerm('finance:files', 'finance:assets')
 */
export function hasPerm(...codes) {
  const perms = getPermissions()
  if (perms.includes('*')) return true
  return codes.some((c) => perms.includes(c))
}

/** 是否拥有任意一项权限（用于父菜单/分组可见性） */
export function hasAnyPerm(codes) {
  return hasPerm(...codes)
}
