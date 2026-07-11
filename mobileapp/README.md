# JobHunter Mobile App

Flutter mobile client for the [JobHunter](https://myjobhunter.in) platform — an end-to-end intelligent job acquisition tool that scrapes real openings, tailors your resume using AI, and sends applications only after your explicit approval.

> **Platform:** Android (iOS build-ready, requires Mac + Xcode)
> **Flutter:** 3.44.6 · Dart · Riverpod · GoRouter
> **Status:** All 16 implementation phases complete. Release APK builds cleanly.

---

## Features

| Feature | Description |
|---|---|
| **Auth** | Email/password login + signup, silent token refresh, secure storage |
| **Job Browser** | Infinite scroll, filter by remote type / job type / email trust / location / experience range, Tinder-style swipe-to-select |
| **Variant Generation** | AI-tailored resume variants per job, approval queue with two-step confirmation |
| **Applications** | Send applications with pre-filled contact details, track status and reply count |
| **Profile** | Full CRUD for experience, education, projects, skills, certifications, social links |
| **Resume Upload** | PDF/DOCX upload with magic-byte validation (max 10 MB) |
| **Dashboard** | Greeting, stats (pending variants, sent today), quick actions |
| **Offline Handling** | Connectivity banner, fail-closed on approve/send actions |
| **Security** | FLAG_SECURE on sensitive screens, HTTPS enforced in release, cleartext blocked |
| **Error Handling** | Global Flutter + platform error boundaries, per-tab isolation, tiered error banners |

---

## Project Structure

```
mobileapp/
├── lib/
│   ├── main.dart                        # Entry point, global error boundaries
│   ├── core/
│   │   ├── network/                     # DioClient, AppError, ApiEndpoints
│   │   ├── router/                      # GoRouter, RouteNames, 17 routes
│   │   ├── storage/                     # SecureStorage (flutter_secure_storage)
│   │   ├── theme/                       # AppColors (#F97316 orange), AppSpacing
│   │   └── utils/                       # FileUtils, DateUtils, SecureScreenMixin
│   ├── features/
│   │   ├── auth/                        # Login, Signup, Splash, SessionNotifier
│   │   ├── jobs/                        # JobListScreen, JobDetailScreen, JobSwipeScreen
│   │   ├── variants/                    # VariantListScreen, VariantDetailScreen, ApprovalFlow
│   │   ├── applications/               # ApplicationListScreen, ApplicationSendSheet
│   │   ├── profile/                     # ProfileScreen, EditProfileScreen, sub-resource CRUD
│   │   ├── resume/                      # ResumeUploadScreen, MasterResumeNotifier
│   │   ├── dashboard/                   # HomeScreen
│   │   └── notifications/               # NotificationService (FCM stub)
│   └── shared/
│       ├── components/                  # 19 reusable components
│       └── layout/                      # MainShell (5-tab BottomNavigationBar)
├── android/
│   ├── app/src/main/AndroidManifest.xml
│   ├── app/src/release/AndroidManifest.xml   # usesCleartextTraffic=false (release only)
│   └── app/src/main/res/xml/network_security_config.xml
└── test/
    ├── unit/                            # Repository unit tests (auth, jobs, variants, applications)
    └── widget/components/               # Component widget tests
```

---

## Getting Started

### Prerequisites

- Flutter 3.44.x (`flutter --version`)
- Android SDK with Build Tools 36 and Platform 36
- Java 17

### Setup

```bash
cd mobileapp
flutter pub get
dart run build_runner build
```

### Run (debug)

```bash
flutter run
```

### Build release APK

```bash
flutter build apk --release
```

> **Note:** The release build currently uses debug signing keys. Configure a proper keystore before distributing. See `NEXT_STEPS.md` in the project root.

### Build App Bundle (Play Store)

```bash
flutter build appbundle --release
```

### Run tests

```bash
flutter test test/unit test/widget/components
```

Expected: **50/50 tests passing**

### Analyze

```bash
dart analyze
```

Expected: **0 errors, 0 warnings**

---

## Key Dependencies

| Package | Purpose |
|---|---|
| `flutter_riverpod` + `riverpod_annotation` | State management (code-gen providers) |
| `go_router` | Declarative routing with auth redirect guard |
| `dio` + `cookie_jar` | HTTP client with persistent cookie jar |
| `flutter_secure_storage` | Encrypted token + session storage |
| `file_selector` | Resume file picking (PDF/DOCX) |
| `connectivity_plus` | Network connectivity stream |
| `freezed` + `json_serializable` | Immutable models with JSON codegen |

---

## Architecture Notes

- **State:** Riverpod with `@riverpod` code generation. All providers are auto-named (e.g. `ProfileNotifier` → `profileProvider`).
- **Navigation:** GoRouter with a `ShellRoute` for the 5-tab shell. Auth guard redirects unauthenticated users to `/login`.
- **Network:** Single `DioClient` singleton. Auth interceptor silently refreshes tokens. Error interceptor maps HTTP status codes to typed `AppError`.
- **Security:** `SecureScreenMixin` sets `FLAG_SECURE` (Android) via MethodChannel on sensitive screens (VariantDetailScreen, ResumeUploadScreen). Release builds block cleartext traffic via manifest overlay.
- **Offline:** `connectivityStreamProvider` (keepAlive) drives `OfflineBanner`. Approve and Send actions are fail-closed when offline.

---

## Environment

The API base URL is configured in `lib/core/network/api_endpoints.dart`. Update `baseUrl` to point to your backend before building for production.

---

## Related

- [Project README](../README.md) — full platform overview
- [NEXT_STEPS.md](../NEXT_STEPS.md) — what to do before Play Store release
- [Implementation Plan](../implementation/FLUTTER_IMPLEMENTATION_PLAN.md)
