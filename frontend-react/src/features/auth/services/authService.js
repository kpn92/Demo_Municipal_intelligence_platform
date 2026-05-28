import client from "../../../api/client.js";
import { ENDPOINTS } from "../../../api/endpoints.js";

function normalizeUser(user) {
  return {
    id: user.id,
    username: user.username,
    name: user.full_name,
    role: user.role,
    roles: user.roles || [],
    modules: user.modules || [],
    sectorScope: user.sector_scope || null,
    isSuperuser: Boolean(user.is_superuser),
  };
}

const authService = {
  async login(username, password) {
    const { data } = await client.post(ENDPOINTS.login, { username, password });
    return normalizeUser(data.user);
  },
};

export default authService;
