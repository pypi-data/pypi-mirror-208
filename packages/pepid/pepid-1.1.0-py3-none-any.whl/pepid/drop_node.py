import struct
import os
import time

if __package__ is None or __package__ == '':
    import blackboard
    import node
else:
    from . import blackboard
    from . import node

class PostNode(node.Node):
    def __init__(self, unix_sock):
        super().__init__(unix_sock)
        self.path = None
        self.messages[0x00] = [None, self.prepare]
        self.messages[0x01] = [None, self.do]

    def do(self, msg):
        start, end = struct.unpack("!QQ", msg[:16])
        strlgt = struct.unpack("!I", msg[16:20])[0]
        col = struct.unpack("!{}s".format(strlgt), msg[20:20+strlgt])[0]

        import glob
        import sqlite3
        all_files = sorted(glob.glob(os.path.join(blackboard.config['data']['workdir'], blackboard.config['data']['database'].split('/')[-1].rsplit('.', 1)[0] + "*pepidpart*.sqlite")))

        if not self.path:
            raise ValueError("'do' message received before 'prepare' message, aborting.")

        for i in range(start, end):
            db = all_files[i]

            conn = sqlite3.connect(db)
            cur = conn.cursor()

            try:
                cur.execute("ALTER TABLE results DROP COLUMN {};".format(col.decode('utf-8')))
                conn.commit()
            except sqlite3.OperationalError as e:
                pass
            finally:
                cur.close()
                conn.close()

    def prepare(self, msg):
        lgt = struct.unpack("!I", msg[:4])[0]
        self.path = struct.unpack("!{}sc".format(lgt), msg[4:])[0].decode('utf-8')
        blackboard.TMP_PATH = self.path
        blackboard.setup_constants()
        blackboard.LOCK = open(os.path.join(blackboard.TMP_PATH, ".lock"), "wb")
        blackboard.prepare_connection()

if __name__ == '__main__':
    node.init(PostNode)
