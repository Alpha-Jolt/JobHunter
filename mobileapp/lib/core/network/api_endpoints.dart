/// All API endpoint paths. Base URL is injected at runtime via dart-define.
abstract class ApiEndpoints {
  // Auth
  static const String register = '/api/auth/register';
  static const String login = '/api/auth/login';
  static const String refresh = '/api/auth/refresh';
  static const String logout = '/api/auth/logout';
  static const String me = '/api/auth/me';
  static const String changePassword = '/api/auth/me/password';

  // Profile
  static const String profileMe = '/api/profile/me';
  static const String profileAvatar = '/api/profile/me/avatar';
  static String publicProfile(String username) => '/api/profile/u/$username';
  static const String profileExperience = '/api/profile/me/experience';
  static String profileExperienceById(String id) =>
      '/api/profile/me/experience/$id';
  static const String profileEducation = '/api/profile/me/education';
  static String profileEducationById(String id) =>
      '/api/profile/me/education/$id';
  static const String profileProjects = '/api/profile/me/projects';
  static String profileProjectById(String id) =>
      '/api/profile/me/projects/$id';
  static const String profileSkills = '/api/profile/me/skills';
  static const String profileCertifications = '/api/profile/me/certifications';
  static const String profileLanguages = '/api/profile/me/languages';
  static const String profileAchievements = '/api/profile/me/achievements';
  static const String profileSocialLinks = '/api/profile/me/social-links';

  // Jobs
  static const String latestJobs = '/api/scraper/latest-jobs';
  static const String jobCounts = '/api/scraper/counts';

  // Resume
  static const String resumeUpload = '/api/resume/upload';

  // AI / Variants
  static const String aiGenerate = '/api/ai/generate';
  static String aiPending(String userId) => '/api/ai/pending/$userId';
  static String aiPreview(String variantId) => '/api/ai/preview/$variantId';
  static String aiVariantToken(String variantId) =>
      '/api/ai/variant/$variantId/token';
  static String aiApprove(String variantId) => '/api/ai/approve/$variantId';
  static String aiReject(String variantId) => '/api/ai/reject/$variantId';

  // Mail / Applications
  static const String mailSend = '/api/mail/send';
  static String mailStatus(String applicationId) =>
      '/api/mail/status/$applicationId';
  static String mailSentToday(String userId) =>
      '/api/mail/sent-today/$userId';
}
