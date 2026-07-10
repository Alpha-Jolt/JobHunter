import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../features/auth/providers/session_provider.dart';
import '../data/job_models.dart';
import '../data/job_repository.dart';

part 'jobs_provider.g.dart';

// ── Infrastructure provider ───────────────────────────────────────────────────

@Riverpod(keepAlive: true)
JobRepository jobRepository(Ref ref) =>
    JobRepository(dioClient: ref.watch(dioClientProvider));

// ── Job list state ────────────────────────────────────────────────────────────

class JobListState {
  const JobListState({
    this.jobs = const [],
    this.filters = JobFilters.empty,
    this.page = 1,
    this.total = 0,
    this.isLoading = false,
    this.isLoadingMore = false,
    this.errorMessage,
  });

  final List<JobRecord> jobs;
  final JobFilters filters;
  final int page;
  final int total;
  final bool isLoading;
  final bool isLoadingMore;
  final String? errorMessage;

  bool get hasMore => jobs.length < total;
  bool get hasError => errorMessage != null;

  JobListState copyWith({
    List<JobRecord>? jobs,
    JobFilters? filters,
    int? page,
    int? total,
    bool? isLoading,
    bool? isLoadingMore,
    String? errorMessage,
    bool clearError = false,
  }) =>
      JobListState(
        jobs: jobs ?? this.jobs,
        filters: filters ?? this.filters,
        page: page ?? this.page,
        total: total ?? this.total,
        isLoading: isLoading ?? this.isLoading,
        isLoadingMore: isLoadingMore ?? this.isLoadingMore,
        errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      );
}

@riverpod
class JobListNotifier extends _$JobListNotifier {
  static const int _pageSize = 20;

  @override
  JobListState build() {
    // Load initial page automatically.
    Future.microtask(() => _loadPage(1, filters: JobFilters.empty));
    return const JobListState(isLoading: true);
  }

  Future<void> _loadPage(int page, {required JobFilters filters}) async {
    final repo = ref.read(jobRepositoryProvider);
    try {
      final result = await repo.getLatestJobs(
        page: page,
        pageSize: _pageSize,
        filters: filters,
      );
      if (page == 1) {
        state = state.copyWith(
          jobs: result.jobs,
          page: result.page,
          total: result.total,
          filters: filters,
          isLoading: false,
          isLoadingMore: false,
          clearError: true,
        );
      } else {
        state = state.copyWith(
          jobs: [...state.jobs, ...result.jobs],
          page: result.page,
          total: result.total,
          isLoadingMore: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        isLoadingMore: false,
        errorMessage: e.toString(),
      );
    }
  }

  /// Pull-to-refresh — resets to page 1 with current filters.
  Future<void> refresh() async {
    state = state.copyWith(isLoading: true, clearError: true);
    await _loadPage(1, filters: state.filters);
  }

  /// Load the next page (infinite scroll).
  Future<void> loadMore() async {
    if (!state.hasMore || state.isLoadingMore || state.isLoading) return;
    state = state.copyWith(isLoadingMore: true);
    await _loadPage(state.page + 1, filters: state.filters);
  }

  /// Apply new filters — resets to page 1.
  Future<void> applyFilters(JobFilters filters) async {
    state = state.copyWith(
      isLoading: true,
      filters: filters,
      clearError: true,
    );
    await _loadPage(1, filters: filters);
  }

  /// Clear all filters and reload.
  Future<void> clearFilters() async => applyFilters(JobFilters.empty);
}

// ── Job counts ────────────────────────────────────────────────────────────────

@riverpod
Future<JobCountsResponse> jobCounts(Ref ref) async {
  return ref.watch(jobRepositoryProvider).getCounts();
}
