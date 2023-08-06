import { BehaviorSubject, Subject } from "rxjs";
import { Component, Input, OnInit } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { DatePipe } from "@angular/common";
import { DeviceCacheStatusTuple } from "../tuples/DeviceCacheStatusTuple";
import { OfflineCacheLoaderStatusTuple } from "@peek/peek_core_device/tuples/OfflineCacheLoaderStatusTuple";
import { OfflineCacheCombinedStatusTuple } from "@peek/peek_core_device/_private/tuples/OfflineCacheCombinedStatusTuple";

@Component({
    selector: "core-device-device-cache-status",
    styleUrls: ["./device-cache-status.component.scss"],
    templateUrl: "./device-cache-status.component.html",
    providers: [DatePipe],
})
export class DeviceCacheStatusComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    readonly combinedStatus$ =
        new BehaviorSubject<OfflineCacheCombinedStatusTuple | null>(null);

    @Input()
    deviceToken$: BehaviorSubject<string>;

    private unsub = new Subject<void>();

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionService: TupleActionPushService,
        private tupleDataObserver: TupleDataObserverService
    ) {
        super();
    }

    ngOnInit() {
        this.deviceToken$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((deviceToken: string) => {
                this.unsub.next();
                this.combinedStatus$.next(null);

                this.tupleDataObserver // Setup a subscription for the device info data
                    .subscribeToTupleSelector(
                        new TupleSelector(
                            OfflineCacheCombinedStatusTuple.tupleName,
                            {
                                deviceToken: deviceToken,
                            }
                        )
                    )
                    .pipe(takeUntil(this.onDestroyEvent))
                    .pipe(takeUntil(this.unsub))
                    .subscribe((tuples: OfflineCacheCombinedStatusTuple[]) => {
                        if (tuples.length !== 0) {
                            this.combinedStatus$.next(tuples[0]);
                        }
                    });
            });
    }
}
