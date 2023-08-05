"""
@time 2023-4-1
@auther yanping

"""

from zerocs.mate import _Mate


class _SnowflakeId(_Mate):
    __work_bits = 5
    __datacenter_bits = 5
    __sequence_bits = 12

    __max_work_id = -1 ^ (-1 << __work_bits)
    __max_datacenter_id = -1 ^ (-1 << __datacenter_bits)

    __work_id_shift = __sequence_bits
    __datacenter_shift = __sequence_bits + __work_bits
    __timestamp_left_shift = __sequence_bits + __work_bits + __datacenter_bits
    __sequence_mask = -1 ^ (-1 << __sequence_bits)

    __timestamp = 1000000000000
    __last_timestamp = -1
    __sequence = 0

    def _get_sequence(self, sequence, last_timestamp, sequence_mask):
        timestamp = self._get_timestamp_millimeter()
        if timestamp < last_timestamp:
            raise ''
        if timestamp == last_timestamp:
            sequence = (sequence + 1) & sequence_mask
            if sequence == 0:
                timestamp = self._get_timestamp_next_second(last_timestamp)
        else:
            sequence = 0
        return sequence, timestamp

    def _get_snowflake_id(self, datacenter_id, worker_id, did_wid):
        if did_wid > 0:
            datacenter_id = did_wid >> 5
            worker_id = did_wid ^ (datacenter_id << 5)

        if worker_id > self.__max_work_id or worker_id < 0:
            raise ValueError('worker_id number overstep the boundary')

        if datacenter_id > self.__max_datacenter_id or datacenter_id < 0:
            raise ValueError('datacenter_id number overstep the boundary')

        self.__sequence, timestamp = self._get_sequence(self.__sequence, self.__last_timestamp, self.__sequence_mask)

        self.__last_timestamp = timestamp
        new_id = ((timestamp - self.__timestamp) << self.__timestamp_left_shift) | \
                 (datacenter_id << self.__datacenter_shift) | \
                 (worker_id << self.__work_id_shift) | self.__sequence
        return f'UID_{new_id}'
