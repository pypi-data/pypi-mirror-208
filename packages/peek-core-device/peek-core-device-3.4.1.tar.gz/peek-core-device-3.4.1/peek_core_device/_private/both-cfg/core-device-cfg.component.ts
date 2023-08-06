import { Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceOfflineCacheService,
    OfflineCacheLoaderStatusTuple,
} from "@peek/peek_core_device";
import { DeviceTupleService } from "@peek/peek_core_device/_private";
import { BehaviorSubject } from "rxjs";
import { DatePipe } from "@angular/common";
import { OfflineCacheStatusTuple } from "@peek/peek_core_device/_private/tuples/OfflineCacheStatusTuple";
import {
    BandwidthStatusI,
    DeviceBandwidthTestService,
} from "@peek/peek_core_device/_private/device-bandwidth-test.service";

@Component({
    selector: "peek-core-device-cfg",
    templateUrl: "core-device-cfg.component.web.html",
    providers: [DatePipe],
})
export class CoreDeviceCfgComponent extends NgLifeCycleEvents {
    offlineLoaderList$: BehaviorSubject<OfflineCacheLoaderStatusTuple[]>;
    offlineCacheStatus$: BehaviorSubject<OfflineCacheStatusTuple | null[]>;

    bandwidthStatus$: BehaviorSubject<BandwidthStatusI>;

    constructor(
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private cacheController: DeviceOfflineCacheService,
        public deviceBandwidthTestService: DeviceBandwidthTestService
    ) {
        super();
        this.offlineLoaderList$ = cacheController.loaderStatus$;
        this.offlineCacheStatus$ = cacheController.status$;
        this.bandwidthStatus$ = deviceBandwidthTestService.status$;

        this.headerService.setTitle("Core Device Config");
    }
}
