# Use Case 003: View Most Accessed URLs

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
UC-003

## Title
View Most Accessed URLs

## Actors
- Dashboard User

## Happy Path
1. The Dashboard User navigates to the statistics web application.
2. The system displays a ranking of the most accessed short URLs along with their access counts.
3. The Dashboard User reviews the statistics.

## Acceptance Criteria

- [ ] Given the statistics page, when the Dashboard User opens it, then the Dashboard User sees a list of the most accessed URLs ranked by access count.
- [ ] Given URLs that have been accessed, when the Dashboard User views the statistics, then each entry shows the short URL, the original long URL, and the number of times it was accessed.
- [ ] Given no URLs have been accessed yet, when the Dashboard User opens the statistics page, then the Dashboard User sees a message indicating no data is available.
