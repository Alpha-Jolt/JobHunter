import '../data/job_models.dart';

/// Holds the queue of jobs the user has swiped right (accepted) during
/// a single swipe session. Max 10 — matches variant budget awareness.
///
/// This is ephemeral UI state: lives only for the duration of the swipe
/// session and is cleared when the user submits or exits.
class SwipeQueueNotifier {
  static const int _maxQueue = 10;

  final List<JobRecord> _accepted = [];

  List<JobRecord> get accepted => List.unmodifiable(_accepted);
  int get count => _accepted.length;
  bool get isFull => _accepted.length >= _maxQueue;

  void accept(JobRecord job) {
    if (!isFull) _accepted.add(job);
  }

  void clear() => _accepted.clear();
}
